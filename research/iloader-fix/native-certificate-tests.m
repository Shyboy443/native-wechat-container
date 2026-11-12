#import "../../LiveContainerSwiftUI/Utilities/LCInstallerCertificate.h"

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        NSCAssert(argc == 2, @"Pass the synthetic installer PKCS#12 path");
        NSData *data = [NSData dataWithContentsOfFile:@(argv[1])];
        NSString *(^team)(NSData *, NSString *) = ^NSString *(NSData *d, NSString *p) { return @"FIXTURETEAM"; };
        NSCAssert(LCCheckInstallerIdentity(data, @"local-fixture-password", @"FIXTURETEAM", team) == nil, @"Valid identity must import");
        NSCAssert(LCCheckInstallerIdentity(data, @"wrong", @"FIXTURETEAM", team) != nil, @"Wrong password must fail");
        NSCAssert(LCCheckInstallerIdentity(data, @"local-fixture-password", @"OTHERTEAM", team) != nil, @"Wrong team must fail");
        NSCAssert(LCCheckInstallerIdentity(NSData.data, @"password", @"FIXTURETEAM", team) != nil, @"Empty identity must fail");
        NSCAssert(LCCheckInstallerIdentity(data, @"", @"FIXTURETEAM", team) != nil, @"Empty password must fail");
        puts("Native certificate validation passed: valid identity, wrong password, wrong team, empty identity, empty password.");
    }
    return 0;
}
