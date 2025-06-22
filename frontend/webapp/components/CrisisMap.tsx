"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { MapPin, AlertTriangle } from "lucide-react"

interface CrisisPoint {
  id: number
  location: string
  disaster_type: string
  aggregate_score: number
  tweet_count: number
  severity: string
  color: string
  x?: number
  y?: number
}

// Built-in coordinate database for common US locations
const US_LOCATION_COORDS: { [key: string]: { x: number; y: number } } = {
  // West Coast
  'Los Angeles': { x: 15, y: 70 },
  'San Francisco': { x: 8, y: 50 },
  'California': { x: 12, y: 60 },
  'Sacramento, California': { x: 10, y: 55 },
  'Santa Rosa': { x: 8, y: 52 },
  'Santa Rosa, CA': { x: 8, y: 52 },
  'Santa Rosa, California': { x: 8, y: 52 },
  'Portland': { x: 12, y: 35 },
  'Seattle': { x: 12, y: 30 },
  
  // Southwest
  'Phoenix': { x: 20, y: 70 },
  'Las Vegas': { x: 15, y: 65 },
  'Denver': { x: 35, y: 55 },
  'Albuquerque': { x: 30, y: 65 },
  
  // Texas
  'Houston': { x: 45, y: 80 },
  'Houston, Texas': { x: 45, y: 80 },
  'Houston, TX': { x: 45, y: 80 },
  'Dallas': { x: 45, y: 75 },
  'San Antonio': { x: 42, y: 82 },
  'Austin': { x: 43, y: 78 },
  'Corpus Christi': { x: 44, y: 85 },
  'Fort Worth': { x: 45, y: 75 },
  
  // Florida
  'Miami': { x: 75, y: 90 },
  'Miami, Florida': { x: 75, y: 90 },
  'Miami, FL': { x: 75, y: 90 },
  'Tampa': { x: 72, y: 85 },
  'Orlando': { x: 73, y: 83 },
  'Orlando, Florida': { x: 73, y: 83 },
  'Jacksonville': { x: 73, y: 78 },
  'Fort Lauderdale': { x: 75, y: 88 },
  'Key West': { x: 75, y: 95 },
  
  // East Coast
  'New York': { x: 68, y: 45 },
  'New York City': { x: 68, y: 45 },
  'Boston': { x: 70, y: 40 },
  'Philadelphia': { x: 68, y: 48 },
  'Washington': { x: 69, y: 55 },
  'Washington DC': { x: 69, y: 55 },
  'Atlanta': { x: 72, y: 70 },
  'Charlotte': { x: 70, y: 65 },
  'Charleston, WV': { x: 70, y: 58 },
  'Richmond, Virginia': { x: 69, y: 60 },
  'Savannah': { x: 73, y: 72 },
  'Savannah, Georgia': { x: 73, y: 72 },
  
  // Midwest
  'Chicago': { x: 60, y: 50 },
  'Detroit': { x: 62, y: 45 },
  'Minneapolis': { x: 55, y: 40 },
  'Kansas City': { x: 50, y: 60 },
  'St. Louis': { x: 55, y: 58 },
  'Milwaukee': { x: 60, y: 47 },
  
  // Caribbean/Territories (approximate positions relative to US map)
  'San Juan': { x: 80, y: 85 },
  'San Juan, Puerto Rico': { x: 80, y: 85 },
  'Charlotte Amalie, U.S. Virgin Islands': { x: 82, y: 88 },
  'St. Martin': { x: 85, y: 85 },
  'Roseau, Dominica': { x: 85, y: 90 },
  'Havana, Cuba': { x: 75, y: 85 },
}

// Cache for dynamically geocoded coordinates
const coordinateCache: { [key: string]: { x: number; y: number } } = {}

// Get coordinates for a location using our backend geocoding service
const getUSCoordinates = async (location: string): Promise<{ x: number; y: number }> => {
  // Check cache first
  if (coordinateCache[location]) {
    return coordinateCache[location]
  }
  
  // Check built-in coordinates database (exact match)
  if (US_LOCATION_COORDS[location]) {
    const coords = US_LOCATION_COORDS[location]
    coordinateCache[location] = coords
    return coords
  }
  
  // Check built-in coordinates database (partial match)
  for (const [key, coords] of Object.entries(US_LOCATION_COORDS)) {
    if (location.toLowerCase().includes(key.toLowerCase()) || 
        key.toLowerCase().includes(location.toLowerCase())) {
      coordinateCache[location] = coords
      return coords
    }
  }
  
  // Use our backend geocoding service as fallback
  try {
    const response = await fetch(
      `http://localhost:8000/api/v1/crisis-map/geocode/${encodeURIComponent(location)}`
    )
    
    if (response.ok) {
      const data = await response.json()
      
      if (data.status === 'success' && data.coordinates) {
        const coords = { x: data.coordinates.x, y: data.coordinates.y }
        coordinateCache[location] = coords
        return coords
      }
    }
  } catch (error) {
    console.warn(`Backend geocoding failed for ${location}:`, error)
  }
  
  // Ultimate fallback to center of US
  const fallbackCoords = { x: 50, y: 60 }
  coordinateCache[location] = fallbackCoords
  return fallbackCoords
}

export default function CrisisMap() {
  const [crisisData, setCrisisData] = useState<CrisisPoint[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchCrisisData = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8000/api/v1/crisis-map/data?limit=50')
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      const rawData = result.data || []
      
      // Geocode all locations
      const geocodedData = await Promise.all(
        rawData.map(async (point: CrisisPoint) => {
          const coords = await getUSCoordinates(point.location)
          return { ...point, x: coords.x, y: coords.y }
        })
      )
      
      setCrisisData(geocodedData)
      
    } catch (err) {
      console.error('Error fetching crisis data:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch crisis data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCrisisData()
  }, [])

  if (loading) {
    return (
      <Card className="border-0 shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center text-[#2B2D42]">
            <MapPin className="h-5 w-5 mr-2 text-[#4B5D67]" />
            Crisis Heat Map
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            <div className="h-80 bg-gray-200 rounded-xl"></div>
            <div className="space-y-2">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="border-0 shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center text-[#2B2D42]">
            <MapPin className="h-5 w-5 mr-2 text-[#4B5D67]" />
            Crisis Heat Map
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={fetchCrisisData} variant="outline">
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border-0 shadow-lg">
      <CardHeader>
        <CardTitle className="flex items-center text-[#2B2D42]">
          <MapPin className="h-5 w-5 mr-2 text-[#4B5D67]" />
          Crisis Heat Map
        </CardTitle>
        <CardDescription className="text-[#2B2D42]/70">
          Real-time emergency monitoring from social media data
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        <div className="relative h-[30rem] bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl overflow-hidden mb-6">
          {/* US Map Background Image */}
          <div 
            className="absolute inset-0 bg-contain bg-center bg-no-repeat opacity-40"
            style={{
              backgroundImage: 'url(/map.png)',
              backgroundSize: '80%'
            }}
          />
          
          <div className="absolute inset-0 p-4">
            {/* Dynamic crisis points from API data */}
            {(() => {
              // Ensure we show both high and low risk points
              const highRisk = crisisData.filter(p => p.severity === 'high').slice(0, 20)
              const lowRisk = crisisData.filter(p => p.severity === 'low').slice(0, 15)
              const mixedData = [...highRisk, ...lowRisk]
              return mixedData
            })().map((point, index) => {
              // Use pre-computed coordinates (fallback to center if not available)
              const x = point.x || 50
              const y = point.y || 60
              
              // Size based on tweet count (high risk larger than low risk, both smaller)
              const baseSize = point.severity === 'high' ? 15 : 12  // High: 15px, Low: 12px (1/4 smaller)
              const size = Math.min(Math.max(Math.log(point.tweet_count + 1) * 1.5 + baseSize, baseSize), 24)
              
              return (
                                 <div
                   key={point.id}
                   className={`absolute group cursor-pointer transform hover:scale-110 transition-transform ${
                     point.severity === 'high' ? 'z-20' : 'z-10'
                   }`}
                   style={{ 
                     left: `${x}%`, 
                     top: `${y}%`,
                     width: `${size}px`,
                     height: `${size}px`
                   }}
                   title={`${point.location} - ${point.disaster_type} (Score: ${point.aggregate_score.toFixed(1)})`}
                 >
                   <div 
                     className="w-full h-full rounded-full border-2 border-white shadow-lg"
                     style={{ 
                       backgroundColor: point.color,
                       opacity: 1  // Make all points fully opaque
                     }}
                   >
                     {/* Only high-risk points get the pulsing animation */}
                     {point.severity === 'high' && (
                       <div className="absolute inset-0 rounded-full animate-ping bg-red-400 opacity-75"></div>
                     )}
                     {/* Add a border for low-risk points to make them more visible */}
                     {point.severity === 'low' && (
                       <div className="absolute inset-0 rounded-full border-2 border-yellow-400"></div>
                     )}
                   </div>
                  
                  {/* Tooltip */}
                  <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-black text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-10">
                    <div className="font-medium">{point.location}</div>
                    <div>{point.disaster_type} - Score: {point.aggregate_score.toFixed(1)}</div>
                    <div>{point.tweet_count} tweets</div>
                  </div>
                </div>
              )
            })}

            {/* User location - Pin style */}
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
              <div className="relative">
                {/* Pin body */}
                <div className="w-6 h-8 bg-[#4B5D67] border-2 border-white shadow-lg" 
                     style={{
                       borderRadius: '50% 50% 50% 50% / 60% 60% 40% 40%',
                       position: 'relative'
                     }}>
                  {/* Pin point */}
                  <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-1/2 w-0 h-0 border-l-2 border-r-2 border-t-4 border-transparent border-t-[#4B5D67]"></div>
                  {/* Center dot */}
                  <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-2 h-2 bg-white rounded-full"></div>
                </div>
              </div>
            </div>

            {/* Legend */}
            <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm rounded-lg p-3 space-y-2">
              <div className="text-xs font-medium text-[#2B2D42] mb-2">Severity Levels</div>
              <div className="flex items-center space-x-2 text-xs">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <span className="text-[#2B2D42]">High (≥60)</span>
              </div>
              <div className="flex items-center space-x-2 text-xs">
                <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <span className="text-[#2B2D42]">Low (&lt;60)</span>
              </div>
              <div className="flex items-center space-x-2 text-xs border-t pt-2">
                <div className="w-3 h-3 bg-[#4B5D67] rounded-full"></div>
                <span className="text-[#2B2D42]">Your Location</span>
              </div>
            </div>
          </div>
        </div>

        {/* Summary Statistics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-[#2B2D42]">{crisisData.length}</div>
            <div className="text-sm text-[#2B2D42]/70">Locations</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-500">
              {crisisData.filter(point => point.severity === 'high').length}
            </div>
            <div className="text-sm text-[#2B2D42]/70">High Risk</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-500">
              {crisisData.filter(point => point.severity === 'low').length}
            </div>
            <div className="text-sm text-[#2B2D42]/70">Low Risk</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-[#2B2D42]">
              {crisisData.reduce((sum, point) => sum + point.tweet_count, 0).toLocaleString()}
            </div>
            <div className="text-sm text-[#2B2D42]/70">Total Tweets</div>
          </div>
        </div>

        {/* Status message */}
        <div className="text-center py-4">
          <p className="text-[#2B2D42]/70">
            {crisisData.length > 0 
              ? `Showing ${Math.min(crisisData.length, 30)} of ${crisisData.length} crisis locations from database`
              : "Loading crisis data from Supabase..."
            }
          </p>
          {crisisData.length > 0 && (
            <p className="text-xs text-[#2B2D42]/50 mt-1">
              {crisisData.filter(p => p.severity === 'high').length} high risk (red, pulsing) • {' '}
              {crisisData.filter(p => p.severity === 'low').length} low risk (yellow, static)
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  )
} 