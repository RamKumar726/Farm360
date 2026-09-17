import { useState, useEffect } from "react";
import { MapPin, Navigation } from "lucide-react";

export default function GPSTracker({ onCapture, showMap = true, farmLat, farmLng }) {
  const [coords, setCoords] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;

  const capture = () => {
    setLoading(true);
    setError(null);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude, accuracy } = pos.coords;
        const captured = { lat: latitude, lng: longitude, accuracy };
        setCoords(captured);
        onCapture?.(captured);
        setLoading(false);
      },
      (err) => {
        setError("GPS access denied or unavailable. Please enable location.");
        setLoading(false);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  const mapUrl = coords && apiKey
    ? `https://maps.googleapis.com/maps/api/staticmap?center=${coords.lat},${coords.lng}&zoom=16&size=400x200&markers=color:red%7C${coords.lat},${coords.lng}${farmLat ? `&markers=color:green%7C${farmLat},${farmLng}` : ""}&key=${apiKey}`
    : null;

  return (
    <div className="space-y-4">
      <button
        onClick={capture}
        disabled={loading}
        className="btn-secondary flex items-center gap-2"
      >
        <Navigation size={16} />
        {loading ? "Acquiring GPS..." : coords ? "Update GPS" : "Capture GPS Location"}
      </button>

      {error && <p className="text-red-400 text-sm">{error}</p>}

      {coords && (
        <div className="glass-panel p-4 space-y-2">
          <div className="flex items-center gap-2 text-green-400">
            <MapPin size={14} />
            <span className="text-sm font-mono">
              {coords.lat.toFixed(6)}, {coords.lng.toFixed(6)}
            </span>
          </div>
          <p className="text-xs text-[#8fac9a]">Accuracy: ±{coords.accuracy?.toFixed(0)}m</p>

          {showMap && mapUrl && (
            <img
              src={mapUrl}
              alt="GPS location map"
              className="rounded-xl w-full mt-2"
              onError={(e) => { e.target.style.display = "none"; }}
            />
          )}
          {showMap && !apiKey && (
            <div className="bg-white/5 rounded-xl p-3 text-center text-[#8fac9a] text-xs">
              📍 Set VITE_GOOGLE_MAPS_API_KEY to show map
            </div>
          )}
        </div>
      )}
    </div>
  );
}
