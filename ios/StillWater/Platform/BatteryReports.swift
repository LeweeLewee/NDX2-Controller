import UIKit
import BackgroundTasks

@MainActor enum BatteryReports {
    static let identifier = "com.ndx2.controller.battery-report"
    static func request(clientID: String) -> BridgeRequest? {
        UIDevice.current.isBatteryMonitoringEnabled = true
        let phone = UIDevice.current
        guard phone.batteryLevel >= 0, phone.batteryState != .unknown else { return nil }
        return BridgeRequest("battery_report",["level":.int(Int((phone.batteryLevel*100).rounded())),
            "charging":.bool(phone.batteryState == .charging || phone.batteryState == .full),"client_id":.string(clientID)])
    }
    static func register() {
        guard !RuntimeMode.demoOnly else { return }
        BGTaskScheduler.shared.register(forTaskWithIdentifier:identifier,using:nil) { task in
            Task { @MainActor in
                guard let processing = task as? BGProcessingTask else { task.setTaskCompleted(success:false); return }
                let operation = Task { @MainActor () -> Bool in
                    do {
                        guard let record = try SecureEnrollment.load(), record.state == "paired", let id = record.device,
                              let req = request(clientID:id), req.args["charging"]?.flag == true else { return false }
                        let client = BridgeClient(record)
                        let reply = try await client.send(req)
                        return reply.outcome == "observed" && reply.data["accepted"].flag == true
                    } catch { return false }
                }
                processing.expirationHandler = { operation.cancel() }
                let success = await operation.value
                processing.setTaskCompleted(success:success && !operation.isCancelled)
                schedule()
            }
        }
    }
    static func schedule() {
        guard !RuntimeMode.demoOnly else { return }
        BGTaskScheduler.shared.cancel(taskRequestWithIdentifier:identifier)
        let request = BGProcessingTaskRequest(identifier:identifier)
        request.requiresExternalPower = true; request.requiresNetworkConnectivity = true
        request.earliestBeginDate = Date(timeIntervalSinceNow:900)
        try? BGTaskScheduler.shared.submit(request) // opportunistic; foreground reporting remains authoritative
    }
}
