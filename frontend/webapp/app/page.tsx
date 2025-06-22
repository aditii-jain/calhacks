import Link from "next/link"
import { Button } from "@/components/ui/button"
import { MapPin, Phone, Shield, Users } from "lucide-react"

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#4B5D67] to-[#3D4C54]">
      {/* Header */}
      <header className="px-4 py-6 md:px-6">
        <nav className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="text-2xl font-medium text-white tracking-wide">sheltr</div>
          <div className="hidden md:flex items-center space-x-8">
            <Link href="#about" className="text-white/80 hover:text-white transition-colors">
              About
            </Link>
            <Link href="#how-it-works" className="text-white/80 hover:text-white transition-colors">
              How it Works
            </Link>
            <Link href="#faq" className="text-white/80 hover:text-white transition-colors">
              FAQ
            </Link>
            <Link href="/auth">
              <Button className="bg-[#F4A261] hover:bg-[#E09248] text-white rounded-full px-6">Get Started</Button>
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <main className="px-4 py-16 md:px-6 md:py-24">
        <div className="max-w-7xl mx-auto">
          <div className="text-center space-y-8">
            <h1 className="text-4xl md:text-6xl font-bold text-white leading-tight">
              When crisis strikes,
              <br />
              <span className="text-[#F4A261]">we speak up.</span>
            </h1>
            <p className="text-xl md:text-2xl text-white/80 max-w-2xl mx-auto">
              Get early warnings and voice guidance in emergencies.
            </p>
            <div className="pt-8">
              <Link href="/auth">
                <Button
                  size="lg"
                  className="bg-[#4B5D67] hover:bg-[#3D4C54] text-white rounded-full px-8 py-4 text-lg font-medium shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"
                >
                  <Phone className="mr-2 h-5 w-5" />
                  Get Voice Alerts
                </Button>
              </Link>
            </div>
          </div>

          {/* Mini Crisis Map Preview */}
          <div className="mt-16 max-w-4xl mx-auto">
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20">
              <h3 className="text-white text-xl font-medium mb-6 text-center">Real-time Crisis Monitoring</h3>
              <div className="relative h-64 bg-[#F9F9F9] rounded-xl overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-blue-100">
                  {/* Simulated map with crisis zones */}
                  <div className="absolute top-1/4 left-1/3 w-16 h-16 bg-red-400/60 rounded-full blur-sm animate-pulse"></div>
                  <div className="absolute bottom-1/3 right-1/4 w-12 h-12 bg-orange-400/60 rounded-full blur-sm animate-pulse"></div>
                  <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                    <MapPin className="h-8 w-8 text-[#4B5D67]" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Features Section */}
      <section className="px-4 py-16 md:px-6 bg-[#F9F9F9]">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-[#2B2D42] mb-4">Crisis assistance that speaks up</h2>
            <p className="text-xl text-[#2B2D42]/70">Smart alerts. Calm voices. Real help.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-[#4B5D67] rounded-full flex items-center justify-center mx-auto">
                <Shield className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-[#2B2D42]">Early Detection</h3>
              <p className="text-[#2B2D42]/70">AI-powered monitoring detects emergencies before they escalate</p>
            </div>

            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-[#F4A261] rounded-full flex items-center justify-center mx-auto">
                <Phone className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-[#2B2D42]">Voice Guidance</h3>
              <p className="text-[#2B2D42]/70">Receive calm, clear instructions through personalized voice calls</p>
            </div>

            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-[#2A9D8F] rounded-full flex items-center justify-center mx-auto">
                <Users className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-[#2B2D42]">Emergency Contacts</h3>
              <p className="text-[#2B2D42]/70">Automatically notify your loved ones when you're in danger</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-4 py-8 md:px-6 bg-[#2B2D42]">
        <div className="max-w-7xl mx-auto text-center">
          <div className="text-2xl font-medium text-white mb-4 tracking-wide">sheltr</div>
          <p className="text-white/60">A voice that guides, not alarms.</p>
        </div>
      </footer>
    </div>
  )
}
