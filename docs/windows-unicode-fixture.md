# Windows Unicode build-root regression

The plugin catalog Unicode-load fixture copies a mock DLL from a CMake-generated
`TARGET_FILE` string. With `/utf-8`, those bytes are UTF-8. Constructing a Windows
`std::filesystem::path` from the ordinary `char*` interprets them using the system
ANSI code page, not necessarily UTF-8. A Chinese build directory can therefore
fail at fixture setup before `inspectPluginDso` or `DataSourceLibrary::load` runs.
Use the C++20 UTF-8 literal type for this known UTF-8 build-time path. The actual
Unicode destination path and both loader assertions are unchanged; missing source
DLLs remain failures with a separate assertion.

The dedicated Windows workflow builds only `plugin_catalog_test` and selects the
two Unicode cases, in a Chinese-and-space build root. It requires exactly two
executed, non-skipped successes and records the runner ANSI code page. No system
code-page setting is changed. This is SDK component evidence, not Qt application,
installer, graphics or release acceptance, and does not approve a native kit.

GoogleTest 1.17 XML output itself uses a narrow path and locale conversion on
Windows. Write instrumentation reports to a separate ASCII evidence directory;
keep the SDK build root and tested DLL destination Unicode. The historical failed
Chinese XML report and failed original fixture remain evidence, not a passing
result. Windows execution of this correction is pending until its CI artifact is
reviewed; Linux source inspection alone cannot establish the Windows outcome.
