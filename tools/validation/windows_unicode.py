# SPDX-License-Identifier: Apache-2.0
"""Isolated Windows Unicode loader regression; never a product/package gate."""
import ctypes
import json
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET


def main():
    if os.name != 'nt':
        raise RuntimeError('Windows MSVC runner required')
    sys.stdout.reconfigure(encoding='utf-8')
    source = Path(__file__).resolve().parents[2]
    root = Path(os.environ['RUNNER_TEMP'])
    build = root / 'SDK 中文 build'
    reports = root / 'sdk-unicode-evidence'
    reports.mkdir(exist_ok=False)
    # Report serialization is instrumentation, not the path under test. Keep
    # GoogleTest's locale-dependent XML writer separate from Unicode DLL paths.
    if not str(reports).isascii():
        raise RuntimeError('XML evidence root must be ASCII for GoogleTest 1.17')
    def run(*args, env=None):
        result = subprocess.run([str(a) for a in args], env=env, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                encoding='utf-8', errors='replace', timeout=1200)
        with (reports / 'commands.log').open('a', encoding='utf-8') as log:
            log.write(json.dumps([str(a) for a in args], ensure_ascii=False) + '\n')
            log.write(result.stdout + '\n')
        print(result.stdout)
        result.check_returncode()
        return result.stdout
    run('conan', 'profile', 'detect', '--force')
    run('conan', 'install', source, '--output-folder', build, '--build=missing',
        '-s', 'build_type=RelWithDebInfo', '-s', 'compiler.cppstd=20',
        '-o', 'plotjuggler_sdk/*:with_tests=True')
    run('cmake', '-S', source, '-B', build, '-G', 'Visual Studio 17 2022', '-A', 'x64',
        '-DCMAKE_TOOLCHAIN_FILE=' + str(build / 'conan_toolchain.cmake'),
        '-DCMAKE_CXX_FLAGS_INIT=/utf-8', '-DPJ_WARNINGS_AS_ERRORS=ON',
        '-DPJ_BUILD_TESTS=ON', '-DPJ_BUILD_PORTED_PLUGINS=OFF')
    run('cmake', '--build', build, '--config', 'RelWithDebInfo',
        '--target', 'plugin_catalog_test', '--parallel', '2')
    cache = (build / 'CMakeCache.txt').read_text(encoding='utf-8')
    flags = next(x for x in cache.splitlines() if x.startswith('CMAKE_CXX_FLAGS:STRING='))
    assert '/utf-8' in flags and '/EHsc' in flags, flags
    env = os.environ.copy()
    env['GTEST_FILTER'] = ('PluginCatalogTest.UnicodeFailureDiagnosticsPreservePath:'
                           'PluginCatalogTest.UnicodeExtensionPathLoadsOnWindows')
    env['GTEST_OUTPUT'] = 'xml:' + str(reports / 'gtest.xml')
    run('ctest', '--test-dir', build, '-C', 'RelWithDebInfo', '-R', '^plugin_catalog_test$',
        '--no-tests=error', '--output-on-failure', '--timeout', '120',
        '--output-junit', reports / 'ctest.xml', env=env)
    cases = ET.parse(reports / 'gtest.xml').getroot().findall('.//testcase')
    assert {c.get('name') for c in cases} == {
        'UnicodeFailureDiagnosticsPreservePath', 'UnicodeExtensionPathLoadsOnWindows'}
    assert len(cases) == 2
    assert all(c.get('status') == 'run' and c.get('result') == 'completed'
               and not any(c.find(t) is not None for t in ('failure', 'error', 'skipped'))
               for c in cases)
    (reports / 'result.json').write_text(json.dumps({
        'passed': 2, 'failed': 0, 'skipped': 0, 'build_root': str(build),
        'windows_acp': ctypes.windll.kernel32.GetACP(),
        'scope': 'SDK Unicode loader only; no Qt application/package acceptance',
    }, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()

