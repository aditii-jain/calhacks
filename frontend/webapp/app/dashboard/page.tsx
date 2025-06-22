"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { MapPin, Phone, Bell, Settings, Shield, Navigation, Users } from "lucide-react"
import CrisisMap from "@/components/CrisisMap"

export default function DashboardPage() {
  const [hasActiveAlert] = useState(true)

  const callHistory = [
    {
      id: 1,
      type: "Fire Alert",
      timestamp: "2 hours ago",
      status: "Shelter info shared",
      location: "Downtown LA",
    },
    {
      id: 2,
      type: "Evacuation Alert",
      timestamp: "1 day ago",
      status: "Contacts notified",
      location: "Westside",
    },
    {
      id: 3,
      type: "Weather Warning",
      timestamp: "3 days ago",
      status: "Safety tips provided",
      location: "Santa Monica",
    },
  ]

  return (
    <div className="min-h-screen bg-[#F9F9F9]">
      {/* Header */}
      <header className="bg-white border-b border-[#4B5D67]/10 px-4 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="text-2xl font-medium text-[#2B2D42] tracking-wide">sheltr</div>
          <div className="flex items-center space-x-4">
            <Button variant="ghost" size="sm" className="text-[#4B5D67] hover:text-[#3D4C54]">
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </Button>
            <div className="w-8 h-8 bg-[#4B5D67] rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">JD</span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Status & Map */}
          <div className="lg:col-span-2 space-y-6">
            {/* Current Status */}
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center text-[#2B2D42]">
                  <Shield className="h-5 w-5 mr-2 text-[#4B5D67]" />
                  Your Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                {hasActiveAlert ? (
                  <div className="space-y-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-3 h-3 bg-[#F4A261] rounded-full animate-pulse"></div>
                      <span className="text-[#2B2D42] font-medium">Fire risk detected 2.1 mi from you</span>
                    </div>
                    <p className="text-[#2B2D42]/70">
                      A wildfire has been reported in Downtown LA. We recommend staying alert and having an evacuation
                      plan ready.
                    </p>
                    <div className="flex flex-wrap gap-3">
                      <Button className="bg-[#2A9D8F] hover:bg-[#238B7A] text-white rounded-full">
                        <Bell className="h-4 w-4 mr-2" />
                        Notify Contacts
                      </Button>
                      <Button
                        variant="outline"
                        className="bg-white text-[#4B5D67] border-[#4B5D67] hover:bg-[#4B5D67] hover:text-white rounded-full"
                      >
                        <Navigation className="h-4 w-4 mr-2" />
                        Find Shelter
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-[#2A9D8F] rounded-full"></div>
                    <span className="text-[#2B2D42] font-medium">No alerts nearby. You're safe.</span>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Crisis Map */}
            <CrisisMap />
          </div>

          {/* Right Column - Call History & Quick Actions */}
          <div className="space-y-6">
            {/* Call History */}
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center text-[#2B2D42]">
                  <Phone className="h-5 w-5 mr-2 text-[#4B5D67]" />
                  Call History
                </CardTitle>
                <CardDescription className="text-[#2B2D42]/70">Recent emergency voice alerts</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {callHistory.map((call) => (
                  <div key={call.id} className="border border-[#4B5D67]/10 rounded-lg p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <Badge variant="secondary" className="bg-[#4B5D67]/10 text-[#4B5D67] hover:bg-[#4B5D67]/20">
                        {call.type}
                      </Badge>
                      <span className="text-xs text-[#2B2D42]/60">{call.timestamp}</span>
                    </div>
                    <p className="text-sm text-[#2B2D42] font-medium">{call.status}</p>
                    <p className="text-xs text-[#2B2D42]/70">{call.location}</p>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="text-[#2B2D42]">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button
                  variant="outline"
                  className="w-full justify-start bg-white text-[#4B5D67] border-[#4B5D67]/20 hover:bg-[#4B5D67]/5"
                >
                  <Users className="h-4 w-4 mr-2" />
                  Update Emergency Contacts
                </Button>
                <Button
                  variant="outline"
                  className="w-full justify-start bg-white text-[#4B5D67] border-[#4B5D67]/20 hover:bg-[#4B5D67]/5"
                >
                  <MapPin className="h-4 w-4 mr-2" />
                  Change Alert Radius
                </Button>
                <Button
                  variant="outline"
                  className="w-full justify-start bg-white text-[#4B5D67] border-[#4B5D67]/20 hover:bg-[#4B5D67]/5"
                >
                  <Bell className="h-4 w-4 mr-2" />
                  Test Voice Alert
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
