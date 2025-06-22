"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { MapPin, Users, Check } from "lucide-react"

export default function OnboardingPage() {
  const [alertRadius, setAlertRadius] = useState("")
  const [contacts, setContacts] = useState([
    { name: "", phone: "" },
    { name: "", phone: "" },
    { name: "", phone: "" },
  ])
  const [isLoading, setIsLoading] = useState(false)

  const updateContact = (index: number, field: "name" | "phone", value: string) => {
    const newContacts = [...contacts]
    newContacts[index][field] = value
    setContacts(newContacts)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1500))
    window.location.href = "/dashboard"
  }

  const isValidPhone = (phone: string) => {
    return phone.length >= 10
  }

  return (
    <div className="min-h-screen bg-[#F9F9F9] py-8 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <div className="text-3xl font-medium text-[#2B2D42] mb-2 tracking-wide">sheltr</div>
          <p className="text-[#2B2D42]/70">Let's set up your emergency preferences</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Location Preferences */}
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center text-[#2B2D42]">
                <MapPin className="h-5 w-5 mr-2 text-[#4B5D67]" />
                Location Preferences
              </CardTitle>
              <CardDescription className="text-[#2B2D42]/70">
                Choose how wide an area you want to monitor for emergencies
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Select value={alertRadius} onValueChange={setAlertRadius} required>
                <SelectTrigger className="border-[#4B5D67]/20 focus:border-[#4B5D67] focus:ring-[#4B5D67]">
                  <SelectValue placeholder="Select alert radius" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="zip">Zip-level alerts (most precise)</SelectItem>
                  <SelectItem value="city">City-level alerts (recommended)</SelectItem>
                  <SelectItem value="county">County-level alerts (widest coverage)</SelectItem>
                </SelectContent>
              </Select>
            </CardContent>
          </Card>

          {/* Emergency Contacts */}
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center text-[#2B2D42]">
                <Users className="h-5 w-5 mr-2 text-[#4B5D67]" />
                Emergency Contacts
              </CardTitle>
              <CardDescription className="text-[#2B2D42]/70">
                Who should we notify if you're in a dangerous zone?
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {contacts.map((contact, index) => (
                <div key={index} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-[#2B2D42]">Contact {index + 1} Name</label>
                    <Input
                      placeholder="Full name"
                      value={contact.name}
                      onChange={(e) => updateContact(index, "name", e.target.value)}
                      className="border-[#4B5D67]/20 focus:border-[#4B5D67] focus:ring-[#4B5D67]"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-[#2B2D42]">Phone Number</label>
                    <div className="relative">
                      <Input
                        type="tel"
                        placeholder="(555) 123-4567"
                        value={contact.phone}
                        onChange={(e) => updateContact(index, "phone", e.target.value)}
                        className="border-[#4B5D67]/20 focus:border-[#4B5D67] focus:ring-[#4B5D67] pr-10"
                      />
                      {isValidPhone(contact.phone) && (
                        <Check className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#2A9D8F]" />
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Button
            type="submit"
            className="w-full bg-[#F4A261] hover:bg-[#E09248] text-white rounded-full py-4 text-lg font-medium transition-all duration-300 hover:shadow-lg"
            disabled={isLoading || !alertRadius}
          >
            {isLoading ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Setting up your account...
              </div>
            ) : (
              <>
                <Check className="mr-2 h-5 w-5" />
                Save Emergency Info
              </>
            )}
          </Button>
        </form>
      </div>
    </div>
  )
}
