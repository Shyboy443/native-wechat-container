# Install the native account-container prototype

This is the compiled LiveContainer-based research prototype with a WeChat account-profile shortcut. The app appears as **LiveContainer** after installation. The package is unsigned and requires signing before installation. It contains the container runtime. A compatible WeChat IPA is imported separately.

## What has been verified

The modified source compiled successfully with Xcode 27.2 in GitHub Actions on 12 November 2026. The job packaged an IPA. Physical-iPhone installation, WeChat login and multiple-account persistence remain untested. Locked-screen remote notifications are outside the accepted scope.

The host app declares iOS 15.0 as its minimum. This metadata alone does not establish compatibility with every iPhone or iOS release.

## Sign and install on an iPhone

1. Set up SideStore using its [official installation guide](https://sidestore.io/). Follow the guide for your computer and iPhone. Apple Account authentication and any required device trust or Developer Mode steps are completed by you.
2. Download `NativeContainer-unsigned.ipa` to the Files app on the iPhone.
3. Import the IPA into SideStore using its app-install control. Let SideStore sign and install it using your Apple Account.
4. When asked about app extensions, keep them. Upstream requires the extensions for multitasking.
5. Open LiveContainer. In its Settings, use **Import Certificate from AltStore/SideStore**, complete the export prompt in the signing app, then return to LiveContainer.
6. Run **JIT-Less Mode Diagnose → Test JIT-Less Mode**. Continue after the diagnostic passes.

These signing steps follow [LiveContainer's standalone installation guide](https://livecontainer.github.io/docs/installation/standalone). Use the upstream-supported AltStore or SideStore versions and setup for your iOS version. This IPA is a sideloading prototype. There is no TestFlight invitation for it.

## Import WeChat and add accounts

1. Obtain a compatible WeChat IPA for your own testing. The host importer requires an unencrypted executable. The standard installed App Store app and a TestFlight invitation do not by themselves supply an importable IPA.
2. Tap **+** in LiveContainer and select that IPA from Files.
3. Open the imported app's settings.
4. For an app with bundle ID `com.tencent.xin`, tap **Add WeChat account profile**. Name the first profile, for example Personal. Repeat for Business. This shortcut turns on app-group separation for each new profile and uses the runtime's existing keychain-group allocation.
5. If that shortcut is absent because the package uses another bundle ID, use the existing new-data-folder/container control instead. Review its data-isolation settings.
6. Select the first container and launch the app. Log in to test account A inside WeChat.
7. Switch to the second container and log in to test account B. Check the visible account identity after every switch.
8. Send a distinct test message with each account. Close and reopen the host, then restart the phone and verify that each profile retains the correct session and history.

Do not treat package import or the appearance of two profiles as proof that two WeChat logins work. That outcome requires the device checks above. The runtime's containers share the host's operating-system sandbox and permissions.

## Homescreen access and multitasking

The runtime provides [home-screen shortcuts](https://livecontainer.github.io/docs/guides/add-to-home-screen) to guest apps/containers. A shortcut opens the container host. The [upstream multitasking guide](https://livecontainer.github.io/docs/guides/multitask) describes shared apps, extension requirements and the supported iOS versions for concurrent guest processes. Device memory and compatibility affect whether concurrent sessions remain usable.

## Source and license

The source is available in the [public build fork](https://github.com/Shyboy443/native-wechat-container/tree/prototype). LiveContainer is AGPL-3.0 licensed. The prototype changes and source license are included in the fork. WeChat itself is a separate dependency and is absent from this package.
