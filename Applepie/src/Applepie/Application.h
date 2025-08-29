#pragma once

#include "Core.h"

namespace Applepie{


    class APPLEPIE_API Application
    {
    public:
	    Application(void);
	    virtual ~Application(void);


		void Run();
    };

	// To be defined in CLIENT
	Application* CreateApplication();
}