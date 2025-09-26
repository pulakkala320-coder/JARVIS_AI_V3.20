///system_quick_actions.cpp
// This file provides optional pybind11-based async exports when pybind11/Python headers
// are available; otherwise it falls back to synchronous implementations to avoid
// include errors in editors/IDEs that don't have Python includePath configured.

#if defined(__has_include)
#  if __has_include(<pybind11/pybind11.h>) && __has_include(<Python.h>)
#    include <Python.h>
#    include <pybind11/pybind11.h>
#    if __has_include(<pybind11/async.h>)
#      include <pybind11/async.h>
#    endif
#    define HAS_PYBIND11 1
#  endif
#endif

#include <Windows.h>
#include <string>
#include <thread>
#include <chrono>
#include <coroutine>

#if !defined(HAS_PYBIND11)
#  include <iostream> // for optional logging in fallback
#endif

#if defined(HAS_PYBIND11)
namespace py = pybind11;
#endif

// Example: async "sleep" coroutine helper (used by both variants)
struct sleep_awaitable {
    std::chrono::milliseconds duration;
    bool await_ready() const noexcept { return false; }
    #if defined(__has_include)
    #  if __has_include(<coroutine>)
    #    include <coroutine>
    #    define _HAS_STD_CORO 1
    #  elif __has_include(<experimental/coroutine>)
    #    include <experimental/coroutine>
    #    define _HAS_STD_CORO 0
    #  else
    #    define _HAS_STD_CORO -1
    #  endif
    #else
    #  define _HAS_STD_CORO -1
    #endif

    #if _HAS_STD_CORO == 1
    using coro_handle_t = std::coroutine_handle<>;
    #elif _HAS_STD_CORO == 0
    using coro_handle_t = std::experimental::coroutine_handle<>;
    #else
    using coro_handle_t = void*;
    #endif

    void await_suspend(coro_handle_t hndl) const {
    #if _HAS_STD_CORO >= 0
        std::thread([hCopy = hndl, d = duration]() mutable {
            std::this_thread::sleep_for(d);
            hCopy.resume();
        }).detach();
    #else
        // No coroutine support available: just sleep on background thread (can't resume).
        std::thread([d = duration]() {
            std::this_thread::sleep_for(d);
        }).detach();
    #endif
    }
    void await_resume() const noexcept {}
};

sleep_awaitable async_sleep(std::chrono::milliseconds d) {
    return sleep_awaitable{d};
}

std::string run_powershell_sync(const std::string &cmd) {
    // Placeholder: synchronous PowerShell call implementation goes here.
    // You can replace this with CreateProcess / piping if you need output capture.
    (void)cmd;
    return "PowerShell command executed (sync)";
}

#if defined(HAS_PYBIND11)

// Async coroutine version wrapping sync call on background thread
// Returns a py::awaitable that Python can await on
py::awaitable<std::string> run_powershell_async(const std::string &cmd) {
    co_return co_await py::async([cmd]() {
        return run_powershell_sync(cmd);
    });
}

// Example bluetooth on/off async
py::awaitable<std::string> bluetooth_set_async(const std::string &state) {
    co_await async_sleep(std::chrono::seconds(1));
    if (state == "on" || state == "enable") {
        co_return "Bluetooth on - simulated async";
    } else {
        co_return "Bluetooth off - simulated async";
    }
}

// Energy saver on/off async
py::awaitable<std::string> energy_saver_on_async() {
    co_await async_sleep(std::chrono::seconds(1));
    system("powercfg /SETDCVALUEINDEX SCHEME_CURRENT SUB_ENERGYSAVER ESBATTTHRESHOLD 100");
    system("powercfg /SETACTIVE SCHEME_CURRENT");
    co_return "Energy Saver चालू हो गया (थ्रेशहोल्ड 100%)";
}

py::awaitable<std::string> energy_saver_off_async() {
    co_await async_sleep(std::chrono::seconds(1));
    system("powercfg /SETDCVALUEINDEX SCHEME_CURRENT SUB_ENERGYSAVER ESBATTTHRESHOLD 0");
    system("powercfg /SETACTIVE SCHEME_CURRENT");
    co_return "Energy Saver बंद हो गया (थ्रेशहोल्ड 0%)";
}

PYBIND11_MODULE(system_quick_actions, m) {
    m.doc() = "C++20 coroutine based async system quick actions for Jarvis";

    m.def("run_powershell", &run_powershell_async, "Async run powershell command");
    m.def("bluetooth_set", &bluetooth_set_async, "🔵 ब्लूटूथ On/Off करो — state: 'on'/'off'");
    m.def("energy_saver_on", &energy_saver_on_async, "⚡ एनर्जी सेवर चालू करो");
    m.def("energy_saver_off", &energy_saver_off_async, "⚡ एनर्जी सेवर बंद करो");
}

#else // fallback when pybind11 or Python headers are not available

// Fallback synchronous functions so the file compiles in an environment without
// Python headers. These can be used from C++ directly; to enable Python bindings
// install/configure pybind11 and Python dev headers and rebuild.
std::string run_powershell(const std::string &cmd) {
    return run_powershell_sync(cmd);
}

std::string bluetooth_set(const std::string &state) {
    std::this_thread::sleep_for(std::chrono::seconds(1));
    if (state == "on" || state == "enable") {
        return "Bluetooth on - simulated (fallback)";
    } else {
        return "Bluetooth off - simulated (fallback)";
    }
}

std::string energy_saver_on() {
    std::this_thread::sleep_for(std::chrono::seconds(1));
    system("powercfg /SETDCVALUEINDEX SCHEME_CURRENT SUB_ENERGYSAVER ESBATTTHRESHOLD 100");
    system("powercfg /SETACTIVE SCHEME_CURRENT");
    return "Energy Saver चालू हो गया (थ्रेशहोल्ड 100%) (fallback)";
}

std::string energy_saver_off() {
    std::this_thread::sleep_for(std::chrono::seconds(1));
    system("powercfg /SETDCVALUEINDEX SCHEME_CURRENT SUB_ENERGYSAVER ESBATTTHRESHOLD 0");
    system("powercfg /SETACTIVE SCHEME_CURRENT");
    return "Energy Saver बंद हो गया (थ्रेशहोल्ड 0%) (fallback)";
}

#endif // HAS_PYBIND11



