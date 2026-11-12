import Combine
import UIKit
import UserNotifications

@MainActor
final class LCNotificationPermission: ObservableObject {
    static let shared = LCNotificationPermission()

    @Published private(set) var status: UNAuthorizationStatus?
    @Published private(set) var isRequesting = false
    @Published private(set) var errorMessage: String?

    func prepare() async {
        guard !isRequesting else { return }
        isRequesting = true
        defer { isRequesting = false }

        let center = UNUserNotificationCenter.current()
        status = await center.notificationSettings().authorizationStatus
        if status == .notDetermined && UIApplication.shared.applicationState == .active {
            errorMessage = nil
            UserDefaults.standard.set(Date(), forKey: "LCNotificationPermissionRequestDate")
            do {
                _ = try await center.requestAuthorization(options: [.alert, .sound, .badge])
            } catch {
                errorMessage = error.localizedDescription
            }
            status = await center.notificationSettings().authorizationStatus
        }
        if let status {
            UserDefaults.standard.set(status.rawValue, forKey: "LCNotificationAuthorizationStatus")
        }
    }

    func openSettings() {
        let address: String
        if #available(iOS 16.0, *) {
            address = UIApplication.openNotificationSettingsURLString
        } else {
            address = UIApplication.openSettingsURLString
        }
        guard let url = URL(string: address) else { return }
        UIApplication.shared.open(url)
    }
}
