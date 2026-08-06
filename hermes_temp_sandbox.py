import math

def main():
    # Current defined exact speed of light in a vacuum
    c_m_s = 299792458  # meters per second
    c_km_s = c_m_s / 1000  # kilometers per second

    # 1 Astronomical Unit (AU) in meters (exact standard definition)
    au_m = 149597870700  # meters
    au_km = au_m / 1000  # kilometers

    # Distance parameters from Sun to Mars
    # Semi-major axis (average distance): ~1.523679 AU
    # Perihelion (closest distance): ~1.3814 AU
    # Aphelion (farthest distance): ~1.6660 AU
    mars_distances = {
        "Average Distance (Semi-major axis)": 1.523679 * au_m,
        "Minimum Distance (Perihelion)": 1.3814 * au_m,
        "Maximum Distance (Aphelion)": 1.6660 * au_m
    }

    print("======================================================================")
    print("HERMES AUTONOMOUS SYSTEM REPORT")
    print("======================================================================\n")
    print("Sir, here are the calculated details regarding the speed of light and")
    print("light propagation time from the Sun to Mars:\n")
    
    print(f"• Current Speed of Light in a Vacuum (c): {c_m_s:,} m/s ({c_km_s:,.3f} km/s)")
    print(f"• 1 Astronomical Unit (AU): {au_m:,} meters ({au_km:,.0f} km)\n")

    print("Travel Time Calculations:")
    print("-" * 50)

    for scenario, dist_m in mars_distances.items():
        dist_km = dist_m / 1000
        time_seconds = dist_m / c_m_s
        minutes = int(time_seconds // 60)
        seconds = time_seconds % 60
        
        print(f"\n{scenario}:")
        print(f"  - Distance: {dist_km:,.0f} km ({dist_m / au_m:.4f} AU)")
        print(f"  - Time: {minutes} minutes and {seconds:.2f} seconds ({time_seconds:.2f} seconds total)")

    print("\n" + "=" * 50)
    print("Sir, on average, it takes approximately 12 minutes and 40 seconds")
    print("for sunlight to reach Mars.")
    print("======================================================================\n")

if __name__ == "__main__":
    main()