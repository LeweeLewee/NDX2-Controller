"""Generate the dependency-free Xcode project deterministically (no XcodeGen)."""
import hashlib
import json
import argparse
from pathlib import Path
import plistlib

ROOT = Path(__file__).resolve().parents[1] / 'ios'


def generate(check=False):
    objects = {}

    def emit(path, raw):
        data = raw.encode('utf-8') if isinstance(raw, str) else raw
        if check:
            if not path.exists() or path.read_bytes() != data:
                raise ValueError(f'Generated project differs: {path.relative_to(ROOT)}')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)

    def uid(name): return hashlib.sha256(name.encode()).hexdigest()[:24].upper()
    def put(identifier, **fields): objects[uid(identifier)] = fields; return uid(identifier)
    def ref(identifier, **fields): return put(identifier, isa='PBXFileReference', **fields)

    groups = []
    products = []
    targets = []
    for name, folder, product, kind in [('StillWater', 'StillWater', 'StillWater.app', 'com.apple.product-type.application'),
                                        ('StillWaterTests', 'StillWaterTests', 'StillWaterTests.xctest', 'com.apple.product-type.bundle.unit-test'),
                                        ('StillWaterUITests', 'StillWaterUITests', 'StillWaterUITests.xctest', 'com.apple.product-type.bundle.ui-testing')]:
        source_build, resource_build, files = [], [], []
        for path in sorted((ROOT / folder).rglob('*')):
            if path.name == 'Info.plist' or any(parent.suffix == '.xcassets' for parent in path.parents): continue
            if not path.is_file() and path.suffix != '.xcassets': continue
            relative = path.relative_to(ROOT).as_posix()
            if path.suffix == '.xcassets': filetype = 'folder.assetcatalog'
            elif path.suffix == '.xcprivacy': filetype = 'text.xml'
            elif path.suffix == '.swift': filetype = 'sourcecode.swift'
            elif path.suffix in ('.ttf', '.otf'): filetype = 'file'
            elif path.suffix in ('.txt', '.json'): filetype = 'text'
            else: continue
            file_id = ref(relative, lastKnownFileType=filetype, path=relative, sourceTree='<group>')
            files.append(file_id)
            build = put(relative + ':build', isa='PBXBuildFile', fileRef=file_id)
            (source_build if path.suffix == '.swift' else resource_build).append(build)
        groups.append(put(name+':group', isa='PBXGroup', children=files, name=name, sourceTree='<group>'))
        sources = put(name+':sources', isa='PBXSourcesBuildPhase', buildActionMask=2147483647, files=source_build, runOnlyForDeploymentPostprocessing=0)
        resources = put(name+':resources', isa='PBXResourcesBuildPhase', buildActionMask=2147483647, files=resource_build, runOnlyForDeploymentPostprocessing=0)
        frameworks = put(name+':frameworks', isa='PBXFrameworksBuildPhase', buildActionMask=2147483647, files=[], runOnlyForDeploymentPostprocessing=0)
        product_ref = ref(name+':product', explicitFileType='wrapper.application' if name == 'StillWater' else 'wrapper.cfbundle', path=product, sourceTree='BUILT_PRODUCTS_DIR')
        products.append(product_ref)
        configurations = []
        for config in ('Debug', 'Release'):
            settings = {'PRODUCT_NAME': '$(TARGET_NAME)', 'PRODUCT_BUNDLE_IDENTIFIER': 'com.riverstone.'+name,
                        'IPHONEOS_DEPLOYMENT_TARGET': '17.0', 'SWIFT_VERSION': '5.0', 'TARGETED_DEVICE_FAMILY': '1',
                        'SDKROOT': 'iphoneos', 'SUPPORTED_PLATFORMS': 'iphoneos iphonesimulator', 'CODE_SIGN_STYLE': 'Automatic',
                        'SWIFT_OPTIMIZATION_LEVEL': '-Onone' if config == 'Debug' else '-O',
                        'SWIFT_ACTIVE_COMPILATION_CONDITIONS': ('DEBUG ' if config == 'Debug' else '') + '$(STILL_WATER_MODE)',
                        'STILL_WATER_MODE': '', 'CURRENT_PROJECT_VERSION': '1', 'MARKETING_VERSION': '0.1.0',
                        'ENABLE_TESTABILITY': 'YES' if config == 'Debug' else 'NO', 'CLANG_ENABLE_MODULES': 'YES',
                        'LD_RUNPATH_SEARCH_PATHS': ['$(inherited)', '@executable_path/Frameworks', '@loader_path/Frameworks']}
            if name == 'StillWater':
                settings['INFOPLIST_FILE'] = 'StillWater/Info.plist'
                settings['ASSETCATALOG_COMPILER_APPICON_NAME'] = 'AppIcon'
                settings['DEBUG_INFORMATION_FORMAT'] = 'dwarf' if config == 'Debug' else 'dwarf-with-dsym'
            else:
                settings['GENERATE_INFOPLIST_FILE'] = 'YES'
                if name == 'StillWaterTests':
                    settings['TEST_HOST'] = '$(BUILT_PRODUCTS_DIR)/StillWater.app/StillWater'
                    settings['BUNDLE_LOADER'] = '$(TEST_HOST)'
                else: settings['TEST_TARGET_NAME'] = 'StillWater'
            configurations.append(put(name+':'+config, isa='XCBuildConfiguration', name=config, buildSettings=settings))
        configlist = put(name+':configs', isa='XCConfigurationList', buildConfigurations=configurations, defaultConfigurationIsVisible=0, defaultConfigurationName='Release')
        dependencies = []
        if name != 'StillWater':
            proxy = put(name+':proxy', isa='PBXContainerItemProxy', containerPortal=uid('project'), proxyType=1, remoteGlobalIDString=uid('StillWater:target'), remoteInfo='StillWater')
            dependencies.append(put(name+':dependency', isa='PBXTargetDependency', target=uid('StillWater:target'), targetProxy=proxy))
        targets.append(put(name+':target', isa='PBXNativeTarget', buildConfigurationList=configlist,
                           buildPhases=[sources, frameworks, resources], buildRules=[], dependencies=dependencies,
                           name=name, productName=name, productReference=product_ref, productType=kind))
    product_group = put('products', isa='PBXGroup', children=products, name='Products', sourceTree='<group>')
    main_group = put('root', isa='PBXGroup', children=groups+[product_group], sourceTree='<group>')
    project_configs = [put('project:'+name, isa='XCBuildConfiguration', name=name, buildSettings={}) for name in ('Debug', 'Release')]
    configlist = put('project:configs', isa='XCConfigurationList', buildConfigurations=project_configs, defaultConfigurationIsVisible=0, defaultConfigurationName='Release')
    project = put('project', isa='PBXProject', attributes={'LastUpgradeCheck': '1600'}, buildConfigurationList=configlist,
                  compatibilityVersion='Xcode 14.0', developmentRegion='en', hasScannedForEncodings=0,
                  knownRegions=['en','Base'], mainGroup=main_group, productRefGroup=product_group, projectDirPath='', projectRoot='', targets=targets)
    def pbx(value):
        if isinstance(value, dict): return '{\n' + '\n'.join(f'{json.dumps(k)} = {pbx(v)};' for k,v in value.items()) + '\n}'
        if isinstance(value, list): return '(' + ', '.join(pbx(v) for v in value) + ')'
        if isinstance(value, int): return str(value)
        return json.dumps(value)
    project_dir = ROOT / 'StillWater.xcodeproj'
    project_dir.mkdir(parents=True, exist_ok=True)
    emit(project_dir/'project.pbxproj','// !$*UTF8*$!\n'+pbx({'archiveVersion':1,'classes':{},'objectVersion':56,'objects':objects,'rootObject':project})+'\n')
    scheme = project_dir/'xcshareddata/xcschemes/StillWater.xcscheme'; scheme.parent.mkdir(parents=True,exist_ok=True)
    def buildable(name):
        filename = 'StillWater.app' if name == 'StillWater' else name+'.xctest'
        return f'<BuildableReference BuildableIdentifier="primary" BlueprintIdentifier="{uid(name+":target")}" BuildableName="{filename}" BlueprintName="{name}" ReferencedContainer="container:StillWater.xcodeproj"/>'
    emit(scheme,f'''<?xml version="1.0" encoding="UTF-8"?>
<Scheme LastUpgradeVersion="1600" version="1.3">
<BuildAction parallelizeBuildables="YES" buildImplicitDependencies="YES"><BuildActionEntries>
<BuildActionEntry buildForTesting="YES" buildForRunning="YES" buildForProfiling="YES" buildForArchiving="YES" buildForAnalyzing="YES">{buildable('StillWater')}</BuildActionEntry>
</BuildActionEntries></BuildAction>
<TestAction buildConfiguration="Debug" selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier="Xcode.IDEFoundation.Launcher.LLDB" shouldUseLaunchSchemeArgsEnv="YES"><Testables>
<TestableReference skipped="NO">{buildable('StillWaterTests')}</TestableReference><TestableReference skipped="NO">{buildable('StillWaterUITests')}</TestableReference>
</Testables><EnvironmentVariables><EnvironmentVariable key="STILL_WATER_FIXTURE" value="1" isEnabled="YES"/></EnvironmentVariables></TestAction>
<LaunchAction buildConfiguration="Debug" selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier="Xcode.IDEFoundation.Launcher.LLDB" launchStyle="0" useCustomWorkingDirectory="NO" ignoresPersistentStateOnLaunch="NO" debugDocumentVersioning="YES" debugServiceExtension="internal" allowLocationSimulation="NO"><BuildableProductRunnable runnableDebuggingMode="0">{buildable('StillWater')}</BuildableProductRunnable></LaunchAction>
<ProfileAction buildConfiguration="Release" shouldUseLaunchSchemeArgsEnv="YES" savedToolIdentifier="" useCustomWorkingDirectory="NO" debugDocumentVersioning="YES"><BuildableProductRunnable runnableDebuggingMode="0">{buildable('StillWater')}</BuildableProductRunnable></ProfileAction>
<AnalyzeAction buildConfiguration="Debug"/><ArchiveAction buildConfiguration="Release" revealArchiveInOrganizer="YES"/>
</Scheme>
''')
    info = {'CFBundleDisplayName':'Still Water','CFBundleName':'StillWater','CFBundleIdentifier':'$(PRODUCT_BUNDLE_IDENTIFIER)',
            'CFBundleExecutable':'$(EXECUTABLE_NAME)','CFBundlePackageType':'APPL','CFBundleShortVersionString':'$(MARKETING_VERSION)','CFBundleVersion':'$(CURRENT_PROJECT_VERSION)',
            'StillWaterBuildMode':'$(STILL_WATER_MODE)',
            'UILaunchScreen':{},'UIApplicationSceneManifest':{'UIApplicationSupportsMultipleScenes':False},
            'UISupportedInterfaceOrientations':['UIInterfaceOrientationLandscapeRight'], 'UIRequiresFullScreen':True,
            'UIStatusBarHidden':True,'UIViewControllerBasedStatusBarAppearance':True,
            'UIBackgroundModes':['processing'],'BGTaskSchedulerPermittedIdentifiers':['com.riverstone.StillWater.battery-report'],
            'NSMicrophoneUsageDescription':'Capture an explicit music search. Cancel discards audio; nothing plays automatically.',
            'NSSpeechRecognitionUsageDescription':'Transcribe music searches on this phone. Audio is not sent to a speech server.',
            'NSLocalNetworkUsageDescription':'Connect to your provisioned authenticated music-control bridge.',
            'UIAppFonts':['InstrumentSerif-Regular.ttf','InstrumentSerif-Italic.ttf','Geist-Regular.ttf','Geist-Medium.ttf'],
            'ITSAppUsesNonExemptEncryption':False}
    emit(ROOT/'StillWater/Info.plist',plistlib.dumps(info,sort_keys=False))
    return objects


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    generate(check=args.check)
    print('PASS iOS project is current' if args.check else 'Generated iOS project, shared scheme and Info.plist')
