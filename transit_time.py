#!/usr/bin/env python3
"""
Swiss Public Transport Travel Time Calculator
Calculate travel times to Lausanne Gare and Rue de la Bergère 2, Meyrin
Uses the free Swiss public transport API - no API key required!
"""

import sys
import requests
import json
from datetime import datetime
import argparse
import urllib.parse

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Default destination addresses
DEFAULT_DESTINATIONS = {
    "Lausanne": "Lausanne",  # Will search for main station
    "Meyrin, Rue de la Bergère": "Meyrin, Bergère"  # Simplified for API search
}

def search_location(query):
    """Search for a location using Swiss transport API"""
    url = "http://transport.opendata.ch/v1/locations"
    params = {"query": query, "type": "all"}
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["stations"]:
            # Return the first (best) match
            station = data["stations"][0]
            return {
                "id": station["id"],
                "name": station["name"],
                "coordinate": station["coordinate"]
            }
    except Exception as e:
        print(f"Error searching for {query}: {e}")
    
    return None

def get_connections(from_location, to_location, arrival_time=None):
    """Get public transport connections between two locations"""
    url = "http://transport.opendata.ch/v1/connections"
    
    params = {
        "from": from_location,
        "to": to_location,
        "limit": 1  # Get next available connection
    }
    
    # If arrival time specified, add it to params
    if arrival_time:
        params["isArrivalTime"] = 1
        params["time"] = arrival_time
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["connections"]:
            conn = data["connections"][0]
            
            # Calculate duration
            departure = datetime.fromisoformat(conn["from"]["departure"].replace("Z", "+00:00"))
            arrival = datetime.fromisoformat(conn["to"]["arrival"].replace("Z", "+00:00"))
            duration = arrival - departure
            duration_mins = int(duration.total_seconds() / 60)
            
            # Format duration
            hours = duration_mins // 60
            mins = duration_mins % 60
            duration_str = f"{hours}h {mins}min" if hours > 0 else f"{mins}min"
            
            # Get journey details
            sections = []
            for section in conn["sections"]:
                if section["journey"]:
                    journey = section["journey"]
                    sections.append({
                        "type": journey.get("category", "Transport"),
                        "number": journey.get("number", ""),
                        "name": journey.get("name", ""),
                        "from": section["departure"]["station"]["name"],
                        "to": section["arrival"]["station"]["name"],
                        "departure": section["departure"]["departure"],
                        "arrival": section["arrival"]["arrival"],
                        "platform": section["departure"].get("platform", "")
                    })
                elif section.get("walk"):
                    walk_duration = section["walk"].get("duration", 0) if section["walk"] else 0
                    if walk_duration:
                        walk_duration = walk_duration // 60
                        sections.append({
                            "type": "Walk",
                            "duration": f"{walk_duration} min",
                            "from": section["departure"]["station"]["name"] if "departure" in section else "",
                            "to": section["arrival"]["station"]["name"] if "arrival" in section else ""
                        })
            
            return {
                "duration": duration_str,
                "departure": conn["from"]["departure"],
                "arrival": conn["to"]["arrival"],
                "transfers": conn.get("transfers", 0),
                "sections": sections,
                "status": "OK"
            }
        else:
            return {"status": "ERROR", "message": "No connections found"}
            
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

class ColoredHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """Custom help formatter with colors"""
    def _format_action(self, action):
        # Get the original formatted action
        parts = super()._format_action(action)
        
        # Color the option strings
        if action.option_strings:
            parts = parts.replace(action.option_strings[0], 
                                f"{Colors.GREEN}{action.option_strings[0]}{Colors.ENDC}")
            if len(action.option_strings) > 1:
                parts = parts.replace(action.option_strings[1], 
                                    f"{Colors.GREEN}{action.option_strings[1]}{Colors.ENDC}")
        
        return parts

def main():
    # Create custom epilog with colors
    epilog = f"""
{Colors.BOLD}{Colors.CYAN}EXAMPLES:{Colors.ENDC}
  
  {Colors.YELLOW}Basic usage (departure now):{Colors.ENDC}
    {Colors.BLUE}%(prog)s "Nyon"{Colors.ENDC}
    {Colors.BLUE}%(prog)s "Rue du Lac 25, Morges"{Colors.ENDC}
    
  {Colors.YELLOW}Arrive at specific time (next weekday):{Colors.ENDC}
    {Colors.BLUE}%(prog)s "Nyon" --arrive 08:30{Colors.ENDC}
    {Colors.BLUE}%(prog)s "Nyon" -a 17:45{Colors.ENDC}
    
  {Colors.YELLOW}Specific date and time:{Colors.ENDC}
    {Colors.BLUE}%(prog)s "Nyon" -a 08:30 --date 2025-07-01{Colors.ENDC}
    
  {Colors.YELLOW}With detailed route information:{Colors.ENDC}
    {Colors.BLUE}%(prog)s "Nyon" -a 08:30 --detailed{Colors.ENDC}
    {Colors.BLUE}%(prog)s "Nyon" -a 08:30 -d{Colors.ENDC}
    
  {Colors.YELLOW}Add custom destinations:{Colors.ENDC}
    {Colors.BLUE}%(prog)s "Nyon" --to "Geneva Airport"{Colors.ENDC}
    {Colors.BLUE}%(prog)s "Nyon" -t "EPFL" -t "Zurich HB"{Colors.ENDC}
    
  {Colors.YELLOW}Only custom destinations (skip defaults):{Colors.ENDC}
    {Colors.BLUE}%(prog)s "Nyon" -t "Bern" -t "Basel SBB" --only{Colors.ENDC}
    
  {Colors.YELLOW}Complete example:{Colors.ENDC}
    {Colors.BLUE}%(prog)s "Place de la Gare 3, Renens" -a 09:00 -d -t "CERN" --date 2025-06-30{Colors.ENDC}
    
{Colors.BOLD}{Colors.CYAN}DEFAULT DESTINATIONS:{Colors.ENDC}
  {Colors.GREEN}•{Colors.ENDC} Lausanne (main station)
  {Colors.GREEN}•{Colors.ENDC} Meyrin, Rue de la Bergère
  
{Colors.BOLD}{Colors.CYAN}NOTES:{Colors.ENDC}
  {Colors.GREEN}•{Colors.ENDC} Times are in 24-hour format (08:30 = 8:30 AM, 17:45 = 5:45 PM)
  {Colors.GREEN}•{Colors.ENDC} When using --arrive without --date, it picks the next weekday (Mon-Fri)
  {Colors.GREEN}•{Colors.ENDC} The script uses the free Swiss public transport API
  {Colors.GREEN}•{Colors.ENDC} No API key required!
        """
    
    parser = argparse.ArgumentParser(
        description=f"{Colors.BOLD}{Colors.HEADER}🚉 Swiss Public Transport Travel Time Calculator{Colors.ENDC}\n"
                    f"{Colors.CYAN}Calculate travel times to default or custom destinations{Colors.ENDC}",
        formatter_class=ColoredHelpFormatter,
        epilog=epilog)
    
    parser.add_argument("address", 
                       help="Starting address or location (e.g., 'Nyon', 'Rue du Lac 25, Morges')")
    parser.add_argument("--detailed", "-d", 
                       action="store_true", 
                       help="Show detailed route information with all connections")
    parser.add_argument("--arrive", "-a", 
                       metavar="HH:MM",
                       help="Calculate to arrive by this time (24-hour format, e.g., 08:30)")
    parser.add_argument("--date", 
                       metavar="YYYY-MM-DD",
                       help="Specific date for arrival (default: next weekday)")
    parser.add_argument("--to", "-t", 
                       metavar="ADDRESS",
                       action="append", 
                       help="Add custom destination(s). Can be used multiple times")
    parser.add_argument("--only", "-o", 
                       action="store_true", 
                       help="Only show custom destinations, skip the defaults")
    
    args = parser.parse_args()
    
    # Prepare destinations
    destinations = {}
    if not args.only:
        destinations.update(DEFAULT_DESTINATIONS)
    
    # Add custom destinations
    if args.to:
        for i, dest in enumerate(args.to, 1):
            destinations[f"Custom destination {i}: {dest}"] = dest
    
    # Handle arrival time
    arrival_datetime = None
    if args.arrive:
        # Parse time
        try:
            hour, minute = map(int, args.arrive.split(':'))
            
            # Get date (default to next weekday if not specified)
            if args.date:
                target_date = datetime.strptime(args.date, "%Y-%m-%d").date()
            else:
                # Find next weekday (Monday-Friday)
                target_date = datetime.now().date()
                while target_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                    target_date = target_date.replace(day=target_date.day + 1)
                
                # If the time has already passed today and it's a weekday, use tomorrow
                now = datetime.now()
                if (target_date == now.date() and 
                    now.hour * 60 + now.minute > hour * 60 + minute and 
                    now.weekday() < 5):
                    target_date = target_date.replace(day=target_date.day + 1)
                    # Skip weekend if needed
                    while target_date.weekday() >= 5:
                        target_date = target_date.replace(day=target_date.day + 1)
            
            arrival_datetime = f"{target_date}T{hour:02d}:{minute:02d}"
            print(f"\n🚉 Swiss Public Transport Travel Times")
            print(f"From: {args.address}")
            print(f"📅 Arriving at destination by: {hour:02d}:{minute:02d} on {target_date.strftime('%A, %Y-%m-%d')}")
        except ValueError:
            print("Error: Invalid time format. Use HH:MM (e.g., 08:30)")
            sys.exit(1)
    else:
        print(f"\n🚉 Swiss Public Transport Travel Times")
        print(f"From: {args.address}")
        print(f"🕐 Departing: Now")
    
    print("=" * 60)
    
    # Search for the starting location
    from_location = search_location(args.address)
    
    if not from_location:
        print(f"Error: Could not find location '{args.address}'")
        print("Try being more specific or use a known station name")
        sys.exit(1)
    
    print(f"Starting point identified as: {from_location['name']}\n")
    
    # Calculate times to each destination
    for dest_name, dest_query in destinations.items():
        print(f"📍 To {dest_name}:")
        print("-" * 40)
        
        to_location = search_location(dest_query)
        
        if not to_location:
            print(f"Error: Could not find destination '{dest_query}'")
            continue
        
        result = get_connections(from_location["name"], to_location["name"], arrival_datetime)
        
        if result["status"] == "OK":
            print(f"⏱️  Duration: {result['duration']}")
            print(f"🔄 Transfers: {result['transfers']}")
            
            if args.detailed and result["sections"]:
                print("\n📋 Route details:")
                for i, section in enumerate(result["sections"], 1):
                    if section["type"] == "Walk":
                        if section.get("from") and section.get("to"):
                            print(f"   {i}. 🚶 Walk: {section['duration']} from {section['from']} to {section['to']}")
                        else:
                            print(f"   {i}. 🚶 Walk: {section['duration']}")
                    else:
                        transport = f"{section['type']} {section.get('number', '')}".strip()
                        if section.get('name'):
                            transport += f" ({section['name']})"
                        platform = f" - Platform {section['platform']}" if section.get('platform') else ""
                        print(f"   {i}. 🚂 {transport}: {section['from']} → {section['to']}{platform}")
                        
                        # Show departure/arrival times for this segment
                        if section.get('departure') and section.get('arrival'):
                            dep = datetime.fromisoformat(section['departure'].replace("Z", "+00:00"))
                            arr = datetime.fromisoformat(section['arrival'].replace("Z", "+00:00"))
                            print(f"      Depart: {dep.strftime('%H:%M')} → Arrive: {arr.strftime('%H:%M')}")
                
                # Show transfer information
                if result["transfers"] > 0:
                    print(f"\n🔄 Transfer details:")
                    for i in range(len(result["sections"]) - 1):
                        current = result["sections"][i]
                        next_section = result["sections"][i + 1]
                        if current["type"] != "Walk" and next_section["type"] != "Walk":
                            transfer_station = current["to"]
                            next_transport = f"{next_section['type']} {next_section.get('number', '')}".strip()
                            print(f"   • At {transfer_station}: Change to {next_transport}")
                            if next_section.get('platform'):
                                print(f"     → Platform {next_section['platform']}")
            
            # Parse and format times
            dep_time = datetime.fromisoformat(result["departure"].replace("Z", "+00:00"))
            arr_time = datetime.fromisoformat(result["arrival"].replace("Z", "+00:00"))
            print(f"\n🕐 Next departure: {dep_time.strftime('%H:%M')} → Arrival: {arr_time.strftime('%H:%M')}")
        else:
            print(f"❌ Error: {result['message']}")
        
        print()
    
    print("=" * 60)
    print(f"🕐 Calculated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n💡 Use {Colors.GREEN}-h{Colors.ENDC} or {Colors.GREEN}--help{Colors.ENDC} to see all options and examples")

if __name__ == "__main__":
    main()