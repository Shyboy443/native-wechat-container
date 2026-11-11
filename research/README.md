# Native WeChat research prototype

Research date 11 November 2026.

This workspace investigates keeping separate WeChat sessions locally on an iPhone. It contains a native-container source prototype and a read-only IPA inspection tool. It has no compiled iPhone build or verified WeChat session.

The user clarified that every account must receive notifications while the phone is locked and the product should work broadly across iPhones. Upstream's absent remote push support makes this container prototype unsuitable as the final product under those requirements. It is retained as an evaluation result.

The private research repository is [Shyboy443/native-wechat-lab](https://github.com/Shyboy443/native-wechat-lab). It was created during this task using the authenticated GitHub account. Two manually dispatched macOS build attempts ended with `startup_failure` before jobs or compiler logs were produced. The underlying startup cause remains unresolved. The native Swift change remains uncompiled. No signing credentials were uploaded.

## What changed

The native runtime is an upstream LiveContainer checkout at commit `9d6ea09b05afa2c8fc537c372795a294db631311`, dated 8 November 2026. The prototype adds an **Add WeChat account profile** action when the imported app identifies as `com.tencent.xin`. It reuses upstream container creation and keychain-group allocation, supplies a readable account name and enables app-group data separation for that new profile.

The upstream runtime remains under its AGPL-3.0 license. The modification is source-visible in the checkout and `native-account-prototype.patch`. It was created for investigation using an existing open-source runtime. The WeChat messaging implementation remains Tencent's executable.

## Evidence for a native route

LiveContainer's source implements multiple app data containers and separate keychain access groups. Its documentation describes multitasking and home-screen shortcuts. Those shortcuts launch guest containers. They are distinct from independently installed copies of WeChat. Upstream also documents absent remote push delivery and shared permissions across guests. [Upstream project](https://github.com/LiveContainer/LiveContainer)

A September 2026 WeChat compatibility report describes successful launch and login, followed by crashes after force-closing and reopening. A maintainer could not reproduce the issue and suggested updating WeChat. This is evidence for attempting a device prototype. It does not establish that two WeChat accounts work reliably. [Compatibility report](https://github.com/LiveContainer/LiveContainer/issues/1581)

## Remaining input dependency

The imported guest still needs a usable native WeChat IPA. The importer explicitly checks Mach-O encryption state and rejects encrypted executables. This is visible in `vendor/LiveContainer/LiveContainerSwiftUI/Models/LCAppInfo.m`. Downloading an archive through an Apple Account does not establish whether that archive is importable.

The Python tool checks the main executable's encryption headers locally. It reads the archive without extracting, modifying, decrypting, signing or uploading it. An unencrypted main executable alone does not establish compatibility. Embedded frameworks, extensions, signing and login still need examination.

All 12 local Python tests passed. The checker also read the official upstream LiveContainer 3.8.0 IPA and identified its arm64 executable, iOS 15.0 minimum and unencrypted main executable. This validates inspection against a real archive. It does not test a WeChat executable or any account functionality.

```powershell
python inspect_ipa.py "C:\path\to\app.ipa"
python -m unittest -v
```

## Build the prototype on a Mac

The development machine used here runs Windows and has no Xcode or iPhone compiler SDK. The native modification has not been compiled. The build script is a prepared macOS build path and remains unverified.

1. Copy this workspace to a Mac with the Xcode version required by the upstream project.
2. Run `bash build-prototype.sh`.
3. The script initializes pinned submodules and attempts to archive the Debug scheme. It packages an unsigned IPA in a fresh `build/native.*` directory.
4. Follow upstream's supported signing and installation process. Its installation guide uses SideStore or AltStore and includes a signing diagnostic.
5. Import a compatible WeChat IPA. Open its app settings and use **Add WeChat account profile** to create separate account containers.

The build script does not create a TestFlight invitation or install the IPA by itself. [Installation requirements](https://livecontainer.github.io/docs/installation) and [signing setup](https://livecontainer.github.io/docs/installation/standalone)

## Device validation

Record the phone model, iOS version, container build and WeChat build before testing. Use two test accounts.

| Check | Status |
| --- | --- |
| Source-level account-profile action added | Prepared |
| IPA inspector handles thin and universal Mach-O headers | Covered by Python tests |
| Native project compiles | Unverified |
| Guest package imports and launches | Unverified |
| Account A and account B both log in | Unverified |
| Data and sessions survive switching and reboot | Unverified |
| Both accounts send and receive while open | Unverified |
| Relaunch after force-close works | Unverified |
| Remote notifications while locked | Unsupported by upstream runtime |
| TestFlight distribution | Unverified and conflicts with documented review restrictions |

For each account, confirm the displayed identity and a unique test conversation. Switch repeatedly and restart the phone. Confirm that neither account inherits the other's login or history. Repeat after force-closing the host and briefly disconnecting the network. App-group separation is a compatibility setting within the host. It does not create an operating-system sandbox between guest apps.

## Push and distribution limits

Apple's notification tokens identify a particular app on a particular device. Repackaging an app with a new identity requires a working provider integration for that new identity. Preserving WeChat's notifications across separately signed copies remains a separate engineering problem. [Apple APNs registration](https://developer.apple.com/documentation/usernotifications/registering-your-app-with-apns)

The container approach imports and executes guest code. Apple's public review rules restrict downloading or executing code that changes app functionality, and TestFlight betas are subject to review guidelines. This makes a TestFlight release of the container approach an unresolved distribution conflict. No review bypass has been implemented. A public installation link is outside the result of this prototype. [Apple review guidelines, sections 2.2 and 2.5](https://developer.apple.com/app-store/review/guidelines/)

## Additional routes examined

Citizen Lab publishes protocol research and instrumentation covering MMTLS. The material examined is research tooling, documentation and traces. A complete native iPhone client with account login, message synchronization and working notifications was not identified in it. [Research source](https://github.com/citizenlab/wechat-security-report)

WeChatFerry's own guide describes a Windows automation framework. A protocol-gateway repository examined provides API examples and explicitly excludes its reverse-engineered implementation. Neither supplies the local native iPhone client required here. [WeChatFerry guide](https://github.com/wechatferry/wechatferry/blob/main/docs/guide.md) and [gateway repository](https://github.com/lichaohuai/wechat-protocol-gateway)

A 2026 USENIX study documents modified native WeChat binaries with injected components. This supports investigating independently installed native copies as another route. The study supplies no verified implementation for this product's complete login and notification requirements. [Primary research](https://cypher-z.github.io/files/usenix26-ios.pdf)

## Conclusion of this investigation

An open-source native-container implementation gives us a concrete way to investigate multiple local sessions without the seller's source code. It still depends on an importable WeChat executable, compatible iOS signing and a real-device test. A complete WeChat-compatible client written entirely from scratch has not been implemented or validated here. The earlier claim that the seller's source project was an absolute requirement was too strong.

Meeting the clarified notification requirement requires a different implementation with working messaging and APNs provider integration for each app identity. No inspected source establishes that capability for this prototype. The existing provider's backend would need to deliver notifications for those identities, or a separately implemented provider would need a working event feed. No such integration was built or tested. Broad iPhone support also requires a stated minimum iOS version and device testing. No universal compatibility claim is supported by this investigation.
