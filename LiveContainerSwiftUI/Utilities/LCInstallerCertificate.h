#import <Foundation/Foundation.h>
#import <Security/Security.h>
#import <TargetConditionals.h>

// The installer puts this identity only into the device-specific signed copy.
// Never include a real identity in a source checkout or public unsigned IPA.
static inline NSString *LCCheckInstallerIdentity(NSData *data, NSString *password,
    NSString *expectedTeam, NSString *(^teamForIdentity)(NSData *, NSString *)) {
    if (data.length == 0 || data.length > 1024 * 1024 || password.length == 0 ||
        password.length > 512 || expectedTeam.length == 0) {
        return @"The installer certificate or signing team is missing or invalid.";
    }
    NSMutableDictionary *options = [@{(__bridge id)kSecImportExportPassphrase: password} mutableCopy];
#if TARGET_OS_OSX
    options[(__bridge id)kSecImportToMemoryOnly] = @YES;
#endif
    CFArrayRef imported = NULL;
    OSStatus status = SecPKCS12Import((__bridge CFDataRef)data,
        (__bridge CFDictionaryRef)options, &imported);
    NSArray *items = CFBridgingRelease(imported);
    if (status != errSecSuccess || items.count != 1 ||
        !items.firstObject[(__bridge id)kSecImportItemIdentity]) {
        return @"The installer certificate could not be unlocked or has no private key. Reinstall with the certificate-fix installer.";
    }
    NSString *team = teamForIdentity(data, password);
    if (![team isEqualToString:expectedTeam]) {
        return @"The installer certificate does not match this app's signing team. Reinstall using the same Apple Account.";
    }
    return nil;
}
