#pragma once

#ifdef AP_PLATFORM_WINDOWS
    #ifdef AP_BUILD_DLL
        #define APPLEPIE_API __declspec(dllexport)
    #else
        #define APPLEPIE_API __declspec(dllimport)
    #endif
#else
    #error Applepie only supports Windows!
#endif