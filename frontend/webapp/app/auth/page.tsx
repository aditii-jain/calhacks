"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowLeft, Phone } from "lucide-react"
import Link from "next/link"

export default function AuthPage() {
  const [step, setStep] = useState<"phone" | "otp">("phone")
  const [phoneNumber, setPhoneNumber] = useState("")
  const [otp, setOtp] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const handlePhoneSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000))
    setStep("otp")
    setIsLoading(false)
  }

  const handleOtpSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000))
    window.location.href = "/onboarding"
  }

  return (
    <div className="min-h-screen bg-[#F9F9F9] flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link
            href="/"
            className="inline-flex items-center text-[#4B5D67] hover:text-[#3D4C54] transition-colors mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to home
          </Link>
          <div className="text-3xl font-medium text-[#2B2D42] mb-2 tracking-wide">sheltr</div>
        </div>

        <Card className="border-0 shadow-lg">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-semibold text-[#2B2D42]">
              {step === "phone" ? "Get Started" : "Verify Your Number"}
            </CardTitle>
            <CardDescription className="text-[#2B2D42]/70">
              {step === "phone"
                ? "We'll use this to send you voice alerts only during a verified emergency."
                : `We sent a code to ${phoneNumber}`}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {step === "phone" ? (
              <form onSubmit={handlePhoneSubmit} className="space-y-6">
                <div className="space-y-2">
                  <label htmlFor="phone" className="text-sm font-medium text-[#2B2D42]">
                    Phone Number
                  </label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#2B2D42]/50" />
                    <Input
                      id="phone"
                      type="tel"
                      placeholder="(555) 123-4567"
                      value={phoneNumber}
                      onChange={(e) => setPhoneNumber(e.target.value)}
                      className="pl-10 border-[#4B5D67]/20 focus:border-[#4B5D67] focus:ring-[#4B5D67]"
                      required
                    />
                  </div>
                </div>
                <Button
                  type="submit"
                  className="w-full bg-[#2A9D8F] hover:bg-[#238B7A] text-white rounded-full py-3 font-medium transition-all duration-300 hover:shadow-lg"
                  disabled={isLoading}
                >
                  {isLoading ? "Sending..." : "Verify My Number"}
                </Button>
              </form>
            ) : (
              <form onSubmit={handleOtpSubmit} className="space-y-6">
                <div className="space-y-2">
                  <label htmlFor="otp" className="text-sm font-medium text-[#2B2D42]">
                    Verification Code
                  </label>
                  <Input
                    id="otp"
                    type="text"
                    placeholder="123456"
                    value={otp}
                    onChange={(e) => setOtp(e.target.value)}
                    className="text-center text-2xl tracking-widest border-[#4B5D67]/20 focus:border-[#4B5D67] focus:ring-[#4B5D67]"
                    maxLength={6}
                    required
                  />
                </div>
                <Button
                  type="submit"
                  className="w-full bg-[#2A9D8F] hover:bg-[#238B7A] text-white rounded-full py-3 font-medium transition-all duration-300 hover:shadow-lg"
                  disabled={isLoading}
                >
                  {isLoading ? "Verifying..." : "Continue"}
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  className="w-full text-[#4B5D67] hover:text-[#3D4C54]"
                  onClick={() => setStep("phone")}
                >
                  Change phone number
                </Button>
              </form>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
