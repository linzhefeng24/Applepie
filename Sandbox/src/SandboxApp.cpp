#include <Applepie.h>

class Sandbox : public Applepie::Application
{
public:
	Sandbox()
	{

	}
	~Sandbox()
	{

	}

};

Applepie::Application* Applepie::CreateApplication()
{
	return new Sandbox();
}
