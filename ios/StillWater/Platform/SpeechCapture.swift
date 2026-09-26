import AVFoundation
import Speech

@MainActor final class SpeechCapture {
    private let engine = AVAudioEngine()
    private var request: SFSpeechAudioBufferRecognitionRequest?, task: SFSpeechRecognitionTask?
    private var token = UUID(), tapped = false
    weak var model: ControllerModel?
    func start() {
        guard !RuntimeMode.demoOnly, RuntimeMode.speechEnabled else { unavailable(); return }
        cancel(); let current = token
        Task {
            let speech = await withCheckedContinuation { continuation in
                SFSpeechRecognizer.requestAuthorization { continuation.resume(returning:$0) }
            }
            let mic = await withCheckedContinuation { continuation in
                AVAudioSession.sharedInstance().requestRecordPermission { continuation.resume(returning:$0) }
            }
            guard token == current, model?.voiceState == "recording", model?.active == true else { return }
            guard speech == .authorized, mic, let recognizer = SFSpeechRecognizer(locale:Locale.current),
                  recognizer.isAvailable, recognizer.supportsOnDeviceRecognition else { unavailable(); return }
            do {
                let session = AVAudioSession.sharedInstance()
                try session.setCategory(.record,mode:.measurement,options:[]); try session.setActive(true)
                let input = engine.inputNode, format = input.outputFormat(forBus:0)
                guard format.sampleRate > 0, format.channelCount > 0 else { throw BridgeFailure.unavailable }
                let req = SFSpeechAudioBufferRecognitionRequest()
                req.requiresOnDeviceRecognition = true; req.shouldReportPartialResults = true
                request = req
                input.installTap(onBus:0,bufferSize:1024,format:format) { [weak self] buffer,_ in
                    req.append(buffer)
                    // Audio activity, not absence of partial-transcript updates, drives silence.
                    if let samples = buffer.floatChannelData?[0], buffer.frameLength > 0 {
                        var energy: Float = 0
                        for index in 0..<Int(buffer.frameLength) { energy += samples[index] * samples[index] }
                        if sqrt(energy / Float(buffer.frameLength)) > 0.015 {
                            Task { @MainActor in
                                guard let self, self.token == current else { return }
                                self.model?.noteSpeechActivity()
                            }
                        }
                    }
                }; tapped = true
                task = recognizer.recognitionTask(with:req) { [weak self] result,error in
                    Task { @MainActor in
                        guard let self, self.token == current, self.model?.voiceState == "recording" else { return }
                        if let result {
                            var text = result.bestTranscription.formattedString
                            while text.utf8.count > 256 { text.removeLast() }
                            self.model?.transcript = text
                            if result.isFinal { self.model?.stopVoice() }
                        } else if error != nil { self.unavailable() }
                    }
                }
                engine.prepare(); try engine.start()
            } catch { unavailable() }
        }
    }
    private func unavailable() { cancel(); model?.voiceState = "unavailable"; model?.transcript = "" }
    func cancel() {
        token = UUID(); engine.stop()
        if tapped { engine.inputNode.removeTap(onBus:0); tapped = false }
        request?.endAudio(); task?.cancel(); task = nil; request = nil
        try? AVAudioSession.sharedInstance().setActive(false,options:.notifyOthersOnDeactivation)
    }
}
