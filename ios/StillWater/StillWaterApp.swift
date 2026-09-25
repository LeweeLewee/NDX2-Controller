import SwiftUI

enum RuntimeMode {
    #if STILL_WATER_PREVIEW
    static let demoOnly = true
    #else
    static let demoOnly = false
    #endif
    static let fixture = demoOnly || ProcessInfo.processInfo.arguments.contains("--fixture") || ProcessInfo.processInfo.environment["STILL_WATER_FIXTURE"] == "1"
}

@MainActor final class AppDelegate: NSObject, UIApplicationDelegate {
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey:Any]? = nil) -> Bool {
        if !RuntimeMode.fixture { BatteryReports.register() }
        return true
    }
    func application(_ application: UIApplication, supportedInterfaceOrientationsFor window: UIWindow?) -> UIInterfaceOrientationMask { .landscapeRight }
}

@main @MainActor struct StillWaterApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) var delegate
    @Environment(\.scenePhase) private var phase
    @StateObject private var model: ControllerModel
    private let speech = SpeechCapture()
    init() {
        let transport: BridgeTransport
        if RuntimeMode.fixture { transport = FixtureTransport() }
        else if let record = try? SecureEnrollment.load(), record.state == "paired" { transport = BridgeClient(record) }
        else { transport = UnconfiguredTransport() }
        _model = StateObject(wrappedValue:ControllerModel(transport:transport))
    }
    var body: some Scene {
        WindowGroup {
            KioskHost(model:model).ignoresSafeArea().persistentSystemOverlays(.hidden).statusBarHidden()
                .onAppear {
                    UIDevice.current.isBatteryMonitoringEnabled = true
                    UIScreen.main.brightness = model.preferences.brightness
                    speech.model = model
                    model.voiceStart = { speech.start() }; model.voiceCancel = { speech.cancel() }
                    model.applyIdlePolicy = { UIApplication.shared.isIdleTimerDisabled = $0 }
                    model.reportBattery = {
                        let id = model.fixture ? "silent-display" : (try? SecureEnrollment.load())?.device ?? "silent-display"
                        if let request = BatteryReports.request(clientID:id) { _ = await model.perform(request) }
                    }
                    let args = ProcessInfo.processInfo.arguments
                    if args.contains("--fixture"), let index = args.firstIndex(of:"--review-state"), args.indices.contains(index+1) {
                        model.snapshotMode = true; model.active = true
                        Task { await ReviewStates.apply(args[index+1],to:model) }
                    } else if phase == .active { model.activate() }
                }
                .onChange(of:phase) { _,value in
                    if value == .active { model.activate() }
                    else { model.deactivate(); if value == .background && !model.fixture && !RuntimeMode.fixture { BatteryReports.schedule() } }
                }
        }
    }
}

struct KioskHost: View {
    @ObservedObject var model: ControllerModel
    var body: some View {
        GeometryReader { proxy in
            ZStack {
                Color.black
                StillWaterView(model:model)
                    .scaleEffect(Design.scale).frame(width:Design.windowWidth,height:Design.windowHeight)
                    .clipped().position(x:proxy.size.width/2,y:proxy.size.height/2)
            }
        }.ignoresSafeArea(.keyboard).background(.black)
    }
}
