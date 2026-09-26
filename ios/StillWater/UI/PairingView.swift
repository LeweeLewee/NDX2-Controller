import SwiftUI
import UniformTypeIdentifiers

struct PairingView: View {
    @ObservedObject var model: ControllerModel
    @State private var origin = ""
    @State private var code = ""
    @State private var certificate: Data?
    @State private var fingerprint = ""
    @State private var showImporter = false
    @State private var confirm = false
    @State private var forget = false
    @State private var replace = false
    @State private var working = false
    @State private var message = RuntimeMode.demoOnly ? "Silent preview: bridge pairing is unavailable in this build." : "Import independently verified bridge trust before pairing."
    var body: some View {
        ScrollView {
            VStack(alignment:.leading,spacing:12) {
                Text(message).font(Design.font(18)).foregroundStyle(Design.ink.opacity(0.7))
                TextField("Bridge address",text:$origin,prompt:Text("https://bridge-host:8991").foregroundStyle(Design.ink.opacity(0.55))).textInputAutocapitalization(.never).autocorrectionDisabled()
                    .font(Design.font(22)).frame(height:56)
                HStack(spacing:12) {
                    Button("Import trust") { showImporter = true }.frame(width:200,height:56)
                    SecureField("One-use pairing code",text:$code).textInputAutocapitalization(.never).autocorrectionDisabled().frame(height:56)
                }.font(Design.font(22))
                if !fingerprint.isEmpty { Text("SHA-256: " + fingerprint).font(Design.font(18)).textSelection(.enabled) }
                HStack(spacing:16) {
                    Button("Approve & pair once") { confirm = true }.disabled(certificate == nil || code.isEmpty || working)
                    Button("Replace trust") { replace = true }.disabled(certificate == nil || working)
                    Button("Forget locally") { forget = true }.disabled(working)
                }.font(Design.font(22)).frame(height:56).disabled(RuntimeMode.demoOnly)
                HStack(spacing:16) {
                    Button("Silent demo") { model.replaceTransport(FixtureTransport()); message = "Silent demo: no device commands or microphone capture." }
                    Button("Use saved pairing") {
                        do {
                            guard let record = try SecureEnrollment.load(), record.state == "paired" else { throw BridgeFailure.notConfigured }
                            model.replaceTransport(BridgeClient(record)); message = "Using saved pairing."
                        } catch { message = "Pairing requires local recovery; no request was sent." }
                    }.disabled(RuntimeMode.demoOnly)
                }.font(Design.font(22)).frame(height:56)
                Text("If pairing is uncertain, inspect and revoke the orphan at the bridge before forgetting locally. Forgetting is not revocation.")
                    .font(Design.font(18)).foregroundStyle(Design.ink.opacity(0.7))
            }.buttonStyle(QuietButtonStyle()).tint(Design.ink).padding(.bottom,16)
        }
        .fileImporter(isPresented:$showImporter,allowedContentTypes:[.data]) { result in
            do {
                let url = try result.get(), granted = url.startAccessingSecurityScopedResource()
                defer { if granted { url.stopAccessingSecurityScopedResource() } }
                let handle = try FileHandle(forReadingFrom:url); defer { try? handle.close() }
                let raw = try handle.read(upToCount:65537) ?? Data()
                let anchors = try Enrollment.certificates(raw)
                certificate = raw
                fingerprint = Enrollment(origin:URL(string:"https://localhost")!,anchors:anchors,state:"pending").trustDigest
                message = "Check the fingerprint through an independent trusted channel."
            } catch { message = "Trust file unavailable or invalid."; certificate = nil; fingerprint = "" }
        }
        .confirmationDialog("Approve this bridge and trust?",isPresented:$confirm,titleVisibility:.visible) {
            Button("Pair once") {
                guard let certificate else { return }; working = true
                let submittedCode = code; code = ""
                Task {
                    defer { working = false }
                    do {
                        let record = try await BridgeClient.pair(origin:origin,certificate:certificate,code:submittedCode)
                        model.replaceTransport(BridgeClient(record)); message = "Paired. Verifying an authoritative snapshot."
                    } catch { message = "Pairing incomplete; inspect local enrollment before trying again." }
                }
            }
        } message: { Text(origin + "\nSHA-256: " + fingerprint) }
        .confirmationDialog("Replace trust for the saved origin?",isPresented:$replace,titleVisibility:.visible) {
            Button("Verify snapshot and replace") {
                guard let certificate else { return }; working = true
                Task {
                    defer { working = false }
                    do { let record = try await BridgeClient.replaceTrust(certificate); model.replaceTransport(BridgeClient(record)); message = "Trust replaced after verification." }
                    catch { message = "Trust verification failed; saved binding retained." }
                }
            }
        } message: { Text("Use only after independently verifying this certificate fingerprint. The saved origin cannot change.\n" + fingerprint) }
        .confirmationDialog("Forget only this phone's pairing?",isPresented:$forget,titleVisibility:.visible) {
            Button("Forget locally",role:.destructive) {
                do { model.deactivate(); try SecureEnrollment.forget(); model.replaceTransport(UnconfiguredTransport()); message = "Local pairing removed. Bridge revocation is separate." }
                catch { message = "Protected storage could not be updated." }
            }
        }
    }
}

@MainActor final class UnconfiguredTransport: BridgeTransport {
    func send(_ request: BridgeRequest) async throws -> BridgeReply { throw BridgeFailure.notConfigured }
    func cancel() {}
}
