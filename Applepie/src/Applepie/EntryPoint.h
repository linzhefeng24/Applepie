#pragma once

#ifdef AP_PLATFORM_WINDOWS

extern Applepie::Application* Applepie::CreateApplication();

int main(int argc, char** argv)
{
	auto app = Applepie::CreateApplication();
	app->Run();
	delete app;
}

#endif