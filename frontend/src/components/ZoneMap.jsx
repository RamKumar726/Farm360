import { useEffect, useRef } from "react";

export default function ZoneMap({ zones = [], farms = [], className = "" }) {
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
  const mapRef = useRef(null);
  const leafletInstance = useRef(null);

  useEffect(() => {
    // If Google Maps API key is present and loaded, use Google Maps
    if (apiKey && window.google && mapRef.current) {
      const gMap = new window.google.maps.Map(mapRef.current, {
        center: farms[0] ? { lat: farms[0].gps_lat, lng: farms[0].gps_lng } : { lat: 17.0005, lng: 81.7800 },
        zoom: 10,
        styles: [
          { featureType: "all", elementType: "geometry.fill", stylers: [{ color: "#1a3c2e" }] },
          { featureType: "water", elementType: "geometry", stylers: [{ color: "#0f1f19" }] },
          { featureType: "road", elementType: "geometry.stroke", stylers: [{ color: "#c9a84c" }] },
        ],
      });

      farms.forEach((farm) => {
        if (farm.gps_lat && farm.gps_lng) {
          new window.google.maps.Marker({
            position: { lat: farm.gps_lat, lng: farm.gps_lng },
            map: gMap,
            title: farm.name || `Farm #${farm.id}`,
          });
        }
      });
      return;
    }

    // Fallback: Leaflet / OpenStreetMap (100% Free, No API Key Required)
    if (!mapRef.current) return;

    // Dynamically inject Leaflet CSS & JS if not already loaded
    if (!document.getElementById("leaflet-css")) {
      const link = document.createElement("link");
      link.id = "leaflet-css";
      link.rel = "stylesheet";
      link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
      document.head.appendChild(link);
    }

    const initLeaflet = () => {
      if (!window.L || !mapRef.current) return;
      if (leafletInstance.current) {
        leafletInstance.current.remove();
      }

      const defaultLat = farms[0]?.gps_lat || 17.0005;
      const defaultLng = farms[0]?.gps_lng || 81.7800;

      const map = window.L.map(mapRef.current).setView([defaultLat, defaultLng], 10);
      leafletInstance.current = map;

      // Dark Mode Tile Layer (CartoDB Dark Matter / OpenStreetMap)
      window.L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>',
        subdomains: "abcd",
        maxZoom: 19,
      }).addTo(map);

      // Add markers for farms
      const customIcon = window.L.divIcon({
        className: "custom-leaflet-marker",
        html: `<div style="background-color:#c9a84c; width:14px; height:14px; border-radius:50%; border:2px solid #ffffff; box-shadow:0 0 10px rgba(201,168,76,0.8);"></div>`,
        iconSize: [14, 14],
        iconAnchor: [7, 7],
      });

      if (farms.length > 0) {
        farms.forEach((f) => {
          const lat = f.gps_lat || 17.0005;
          const lng = f.gps_lng || 81.7800;
          window.L.marker([lat, lng], { icon: customIcon })
            .addTo(map)
            .bindPopup(`<b style="color:#1a3c2e;">${f.name || "Managed Farm"}</b><br/>Location: ${f.location || "Godavari Region"}`);
        });
      } else {
        // Default pin
        window.L.marker([17.0005, 81.7800], { icon: customIcon })
          .addTo(map)
          .bindPopup("<b>Rajahmundry Main Zone Farm</b>");
      }
    };

    if (window.L) {
      initLeaflet();
    } else {
      const script = document.createElement("script");
      script.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
      script.onload = initLeaflet;
      document.body.appendChild(script);
    }

    return () => {
      if (leafletInstance.current) {
        leafletInstance.current.remove();
        leafletInstance.current = null;
      }
    };
  }, [farms, apiKey]);

  return (
    <div
      ref={mapRef}
      className={`rounded-2xl overflow-hidden border border-white/10 ${className}`}
      style={{ minHeight: 320, width: "100%" }}
    />
  );
}
