# 🚉 Swiss Public Transport Travel Time Calculator

A command-line tool to calculate public transport travel times in Switzerland. Perfect for commuters who need to check travel times to multiple destinations, plan their arrival times, or compare different commute options.

## ✨ Features

- 🚍 **Real-time public transport information** using the free Swiss transport API
- ⏰ **Arrival time planning** - specify when you need to arrive
- 📍 **Multiple destinations** - check travel times to several places at once
- 🔄 **Detailed route information** - see all connections, platforms, and transfer points
- 🎨 **Colorful output** - easy-to-read terminal display
- 🆓 **No API key required** - uses the open Swiss transport data

## 📋 Prerequisites

- Python 3.6 or higher
- `requests` library

## 🚀 Installation

1. Clone or download the `transit_time.py` script

2. Install the required dependency:
```bash
pip install requests
```

3. Make the script executable (optional, for Unix-like systems):
```bash
chmod +x transit_time.py
```

## 💻 Usage

### Basic Usage

Check travel times departing now:
```bash
python transit_time.py "Nyon"
python transit_time.py "Rue du Lac 25, Morges"
```

### Arrival Time Planning

Arrive at your destination by a specific time:
```bash
python transit_time.py "Nyon" --arrive 08:30
python transit_time.py "Nyon" -a 17:45
```

### Specific Date

Plan for a specific date:
```bash
python transit_time.py "Nyon" -a 08:30 --date 2025-07-01
```

### Detailed Route Information

See complete journey details with platforms and connections:
```bash
python transit_time.py "Nyon" -a 08:30 --detailed
python transit_time.py "Nyon" -a 08:30 -d
```

### Custom Destinations

Add your own destinations:
```bash
python transit_time.py "Nyon" --to "Geneva Airport"
python transit_time.py "Nyon" -t "EPFL" -t "Zurich HB"
```

Skip default destinations and only use custom ones:
```bash
python transit_time.py "Nyon" -t "Bern" -t "Basel SBB" --only
```

### Complete Example

```bash
python transit_time.py "Place de la Gare 3, Renens" -a 09:00 -d -t "CERN" --date 2025-06-30
```

## 📍 Default Destinations

The script calculates travel times to these destinations by default:
- **Lausanne** (main station)
- **Meyrin, Rue de la Bergère**

## 🎯 Command-Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `address` | | Starting address or location (required) |
| `--arrive` | `-a` | Calculate to arrive by this time (HH:MM format) |
| `--date` | | Specific date (YYYY-MM-DD format) |
| `--detailed` | `-d` | Show detailed route information |
| `--to` | `-t` | Add custom destination(s) |
| `--only` | `-o` | Only show custom destinations |
| `--help` | `-h` | Show help message |

## 📝 Notes

- Times are in 24-hour format (08:30 = 8:30 AM, 17:45 = 5:45 PM)
- When using `--arrive` without `--date`, it automatically picks the next weekday (Mon-Fri)
- The script uses the free [Swiss public transport API](https://transport.opendata.ch/)
- No API key or registration required

## 🔧 Troubleshooting

### Location not found
If the script can't find your address:
- Try being more specific (add city name)
- Use a known station name
- Check spelling

### No connections found
- The API might be temporarily unavailable
- Try a different time or date
- Check if the destination exists in the Swiss transport network

## 📊 Example Output

```
🚉 Swiss Public Transport Travel Times
From: Nyon
📅 Arriving at destination by: 08:30 on Thursday, 2025-06-26
============================================================
Starting point identified as: Nyon

📍 To Lausanne:
----------------------------------------
⏱️  Duration: 27min
🔄 Transfers: 0

📋 Route details:
   1. 🚂 RE (RegioExpress): Nyon → Lausanne - Platform 2
      Depart: 08:01 → Arrive: 08:28

🕐 Next departure: 08:01 → Arrival: 08:28

📍 To Meyrin, Rue de la Bergère:
----------------------------------------
⏱️  Duration: 1h 11min
🔄 Transfers: 2

🕐 Next departure: 07:12 → Arrival: 08:23
============================================================
🕐 Calculated at: 2025-06-25 17:05:05

💡 Use -h or --help to see all options and examples
```

## 🙏 Acknowledgments

- [Swiss Public Transport Open Data](https://transport.opendata.ch/) for providing the free API
- The Swiss public transport system for being amazingly punctual 🚂