#if defined(__has_include)
#  if __has_include(<pybind11/pybind11.h>) && __has_include(<Python.h>)
#    include <pybind11/pybind11.h>
#    define HAVE_PYBIND11 1
#  endif
#endif

#include <windows.h>
#if defined(__has_include)
#  if __has_include(<mmdeviceapi.h>) && __has_include(<endpointvolume.h>)
#    include <mmdeviceapi.h>
#    include <endpointvolume.h>
#    define HAVE_WASAPI 1
#  endif
#endif

// ----------- Volume Controls ----------
#ifdef HAVE_WASAPI
float get_volume() {
    HRESULT hr;
    CoInitialize(NULL);

    IMMDeviceEnumerator* deviceEnumerator = NULL;
    IMMDevice* defaultDevice = NULL;
    IAudioEndpointVolume* endpointVolume = NULL;

    hr = CoCreateInstance(__uuidof(MMDeviceEnumerator), NULL,
        CLSCTX_ALL, __uuidof(IMMDeviceEnumerator),
        (void**)&deviceEnumerator);

    if (FAILED(hr)) { CoUninitialize(); return -1; }

    hr = deviceEnumerator->GetDefaultAudioEndpoint(eRender, eConsole, &defaultDevice);
    deviceEnumerator->Release();

    if (FAILED(hr)) { CoUninitialize(); return -1; }

    hr = defaultDevice->Activate(__uuidof(IAudioEndpointVolume),
        CLSCTX_ALL, NULL, (void**)&endpointVolume);
    defaultDevice->Release();

    if (FAILED(hr)) { CoUninitialize(); return -1; }

    float currentVolume = 0.0f;
    endpointVolume->GetMasterVolumeLevelScalar(&currentVolume);

    endpointVolume->Release();
    CoUninitialize();

    return currentVolume * 100.0f; // percentage
}

void set_volume(float level) {
    if (level < 0.0f) level = 0.0f;
    if (level > 100.0f) level = 100.0f;

    HRESULT hr;
    CoInitialize(NULL);

    IMMDeviceEnumerator* deviceEnumerator = NULL;
    IMMDevice* defaultDevice = NULL;
    IAudioEndpointVolume* endpointVolume = NULL;

    hr = CoCreateInstance(__uuidof(MMDeviceEnumerator), NULL,
        CLSCTX_ALL, __uuidof(IMMDeviceEnumerator),
        (void**)&deviceEnumerator);

    if (FAILED(hr)) { CoUninitialize(); return; }

    hr = deviceEnumerator->GetDefaultAudioEndpoint(eRender, eConsole, &defaultDevice);
    deviceEnumerator->Release();

    if (FAILED(hr)) { CoUninitialize(); return; }

    hr = defaultDevice->Activate(__uuidof(IAudioEndpointVolume),
        CLSCTX_ALL, NULL, (void**)&endpointVolume);
    defaultDevice->Release();

    if (FAILED(hr)) { CoUninitialize(); return; }

    endpointVolume->SetMasterVolumeLevelScalar(level / 100.0f, NULL);

    endpointVolume->Release();
    CoUninitialize();
}
#else
// WASAPI headers not available; provide safe fallbacks so the TU compiles.
float get_volume() {
    (void)0;
    return -1; // indicate unavailable
}
void set_volume(float level) {
    (void)level;
}
#endif

// ----------- Bind to Python or provide fallback C exports -----------
#ifdef HAVE_PYBIND11
PYBIND11_MODULE(cpp_system_controls, m) {
    m.doc() = "Fast C++ system controls for Jarvis";

    m.def("get_volume", &get_volume, "Get current system volume (0-100)");
    m.def("set_volume", &set_volume, "Set system volume (0-100)");
}
#else
// Provide simple C-exported wrappers so the functionality is still usable for testing or linking
// even when pybind11 headers aren't available to the editor/IDE.
extern "C" __declspec(dllexport) float get_volume_c() { return get_volume(); }
extern "C" __declspec(dllexport) void set_volume_c(float level) { set_volume(level); }
#endif

