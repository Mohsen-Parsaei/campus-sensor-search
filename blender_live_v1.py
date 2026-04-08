# Campus Digital Twin - Live Sensor Search Panel for Blender
# Fetches real-time data from EmpathicBuilding API
# Run in Blender Scripting tab, then press N in 3D Viewport -> CiC Twin tab

import bpy
import json
import os
import threading
import urllib.request
import urllib.error

# --- CONFIG ---
EB_TOKEN = "8053a0ed-3584-40a6-911f-dbfc34a45dc1"
EB_BASE  = "https://eu-api.empathicbuilding.com/v1"
EB_ORG   = "10"

# How often to refresh in seconds (60 = every minute)
REFRESH_INTERVAL = 60

CO2_GOOD   = 700
CO2_MEDIUM = 1000

# Fallback snapshot data (real values from March 2026)
SNAPSHOT_DATA = {
    "A1017": {"id": "A1017", "dis": "Ruokailutilat 6 hlo", "co2": 390.0, "temp": 22.2, "occ": 1},
    "A1018": {"id": "A1018", "dis": "Ruokailutilat 6 hlo", "co2": 425.0, "temp": 22.0, "occ": 1},
    "A1504": {"id": "A1504", "dis": "Kaytava", "co2": 0, "temp": 21.9, "occ": 0},
    "A1013": {"id": "A1013", "dis": "Ruokailutilat 25 hlo", "co2": 429.0, "temp": 23.3, "occ": 1},
    "A1014": {"id": "A1014", "dis": "Ruokailutilat 30 hlo", "co2": 406.0, "temp": 23.1, "occ": 0},
    "A1015": {"id": "A1015", "dis": "Ruokailutilat 6 hlo", "co2": 396.0, "temp": 22.5, "occ": 1},
    "A1016": {"id": "A1016", "dis": "Ruokailutilat 6 hlo", "co2": 407.0, "temp": 24.9, "occ": 0},
    "A1012": {"id": "A1012", "dis": "Ruokailutilat", "co2": 0, "temp": 22.3, "occ": 0},
    "B1003": {"id": "B1003", "dis": "Kuntosali, kuntoutukseen sopivin laittein", "co2": 0, "temp": 21.4, "occ": 0},
    "B1005": {"id": "B1005", "dis": "Luentosali 120 paikkaa", "co2": 405.0, "temp": 20.8, "occ": 0},
    "B1006": {"id": "B1006", "dis": "Optikkomyymala NT", "co2": 403.0, "temp": 22.5, "occ": 1},
    "B1007": {"id": "B1007", "dis": "Optikkomyymala HIONTA", "co2": 403.0, "temp": 23.2, "occ": 0},
    "B1008": {"id": "B1008", "dis": "Optikkomyymala", "co2": 402.0, "temp": 21.6, "occ": 1},
    "B1045": {"id": "B1045", "dis": "Aistihuone", "co2": 403.0, "temp": 21.3, "occ": 0},
    "B1016.2": {"id": "B1016.2", "dis": "Jalkaterapia, 2 op", "co2": 408.0, "temp": 21.9, "occ": 0},
    "B1016.3": {"id": "B1016.3", "dis": "Jalkaterapia, 2 op", "co2": 402.0, "temp": 22.3, "occ": 0},
    "B1016.4": {"id": "B1016.4", "dis": "Jalkaterapia, 4 op", "co2": 402.0, "temp": 22.2, "occ": 0},
    "B1016.5": {"id": "B1016.5", "dis": "Jalkaterapia, 2 op", "co2": 409.0, "temp": 21.6, "occ": 0},
    "B1016.6": {"id": "B1016.6", "dis": "Jalkaterapia, 2 op", "co2": 401.0, "temp": 22.0, "occ": 0},
    "B1016.7": {"id": "B1016.7", "dis": "Jalkaterapia, 2 op", "co2": 409.0, "temp": 22.6, "occ": 0},
    "B1016.8": {"id": "B1016.8", "dis": "Jalkaterapia, 4 op", "co2": 399.0, "temp": 22.8, "occ": 0},
    "B1016.9": {"id": "B1016.9", "dis": "Jalkaterapia, 2 op", "co2": 404.0, "temp": 22.6, "occ": 0},
    "B1016.10": {"id": "B1016.10", "dis": "Jalkaterapia, 2 op", "co2": 402.0, "temp": 22.2, "occ": 0},
    "B1016.11": {"id": "B1016.11", "dis": "Jalkaterapia, 2 op", "co2": 405.0, "temp": 22.3, "occ": 0},
    "B1016.12": {"id": "B1016.12", "dis": "Jalkaterapia, 2 op", "co2": 409.0, "temp": 21.2, "occ": 0},
    "B1016.13": {"id": "B1016.13", "dis": "Jalkaterapia, 2 op", "co2": 406.0, "temp": 22.4, "occ": 0},
    "B1018": {"id": "B1018", "dis": "Suun hoidon opetusklinikka/ RTG, 3 op", "co2": 398.0, "temp": 21.4, "occ": 0},
    "B1020": {"id": "B1020", "dis": "Liikelaboratorio, 30 op", "co2": 404.0, "temp": 20.4, "occ": 1},
    "B1029": {"id": "B1029", "dis": "Kotikulma, OH", "co2": 402.0, "temp": 21.1, "occ": 0},
    "B1013.2": {"id": "B1013.2", "dis": "Positia, terapia, 2 op", "co2": 394.0, "temp": 22.2, "occ": 0},
    "B1013.3": {"id": "B1013.3", "dis": "Positia, terapia, 2 op", "co2": 387.0, "temp": 22.3, "occ": 0},
    "B1013.4": {"id": "B1013.4", "dis": "Positia, terapia, 2 op", "co2": 391.0, "temp": 22.0, "occ": 1},
    "B1013.5": {"id": "B1013.5", "dis": "Positia, terapia, 2 op", "co2": 383.0, "temp": 22.2, "occ": 0},
    "B1013.6": {"id": "B1013.6", "dis": "Positia, terapia, 2 op", "co2": 392.0, "temp": 22.3, "occ": 0},
    "B1013.7": {"id": "B1013.7", "dis": "Positia, terapia, 2 op", "co2": 397.0, "temp": 22.4, "occ": 0},
    "B1013.8": {"id": "B1013.8", "dis": "Positia, terapia, 2 op", "co2": 399.0, "temp": 22.2, "occ": 0},
    "B1013.9": {"id": "B1013.9", "dis": "Positia, terapia, 2 op", "co2": 394.0, "temp": 22.2, "occ": 0},
    "B1013.10": {"id": "B1013.10", "dis": "Positia, terapia, 2 op", "co2": 396.0, "temp": 21.9, "occ": 0},
    "B1013.11": {"id": "B1013.11", "dis": "Positia, terapia, 2 op", "co2": 392.0, "temp": 21.4, "occ": 0},
    "B1013.12": {"id": "B1013.12", "dis": "Positia, terapia, 2 op", "co2": 399.0, "temp": 21.4, "occ": 0},
    "B1013.13": {"id": "B1013.13", "dis": "Positia, terapia, 2 op", "co2": 419.0, "temp": 20.8, "occ": 0},
    "B1013.14": {"id": "B1013.14", "dis": "Positia, terapia, 2 op", "co2": 410.0, "temp": 20.8, "occ": 0},
    "B1013.15": {"id": "B1013.15", "dis": "Positia, terapia, 2 op", "co2": 385.0, "temp": 21.6, "occ": 0},
    "B1013.16": {"id": "B1013.16", "dis": "Positia, terapia, 2 op", "co2": 394.0, "temp": 21.5, "occ": 0},
    "B1013.17": {"id": "B1013.17", "dis": "Positia, terapia, 2 op", "co2": 394.0, "temp": 21.7, "occ": 0},
    "B1014": {"id": "B1014", "dis": "Positian asiakastilat, terapia, 6 op", "co2": 393.0, "temp": 22.3, "occ": 1},
    "C1001": {"id": "C1001", "dis": "Demoluokka, 100 op", "co2": 397.0, "temp": 21.6, "occ": 0},
    "C1501": {"id": "C1501", "dis": "Kaytava", "co2": 405.0, "temp": 22.9, "occ": 1},
    "C1504": {"id": "C1504", "dis": "Yleisoaula", "co2": 410.0, "temp": 22.3, "occ": 0},
    "C1505": {"id": "C1505", "dis": "Avoin opiskelu", "co2": 404.0, "temp": 21.7, "occ": 1},
    "D1002": {"id": "D1002", "dis": "Auditorio 200 paikkaa", "co2": 401.0, "temp": 21.8, "occ": 0},
    "D1506": {"id": "D1506", "dis": "Megora (kahvio)", "co2": 403.0, "temp": 23.3, "occ": 1},
    "B1502": {"id": "B1502", "dis": "Avoin opiskelu", "co2": 0, "temp": 21.0, "occ": 0},
    "B1605": {"id": "B1605", "dis": "Kerrosjakamo", "co2": 0, "temp": 22.9, "occ": 0},
    "B1704": {"id": "B1704", "dis": "Kompressorihuone", "co2": 0, "temp": 19.0, "occ": 0},
    "B1015": {"id": "B1015", "dis": "Varasto, Positia, 6op", "co2": 0, "temp": 19.9, "occ": 0},
    "B1019": {"id": "B1019", "dis": "Opetusklinikan varasto, 3 op", "co2": 0, "temp": 20.1, "occ": 0},
    "B1017": {"id": "B1017", "dis": "Suun hoidon opetusklinikka, n.50 op", "co2": 329.0, "temp": 20.8, "occ": 0},
    "C1003": {"id": "C1003", "dis": "Vahtimestari", "co2": 0, "temp": 22.0, "occ": 0},
    "C1701": {"id": "C1701", "dis": "Sahkot.", "co2": 0, "temp": 23.1, "occ": 0},
    "A1010": {"id": "A1010", "dis": "Iso auditorio, 275 paikkaa", "co2": 436.2, "temp": 21.3, "occ": 0},
    "D1005": {"id": "D1005", "dis": "Ryhmatyotilat", "co2": 0, "temp": 23.6, "occ": 0},
    "D1006": {"id": "D1006", "dis": "Ryhmatyotilat 4 op.", "co2": 0, "temp": 26.1, "occ": 0},
    "D1007": {"id": "D1007", "dis": "Ryhmatyotilat 4 op.", "co2": 0, "temp": 25.3, "occ": 0},
    "D1008": {"id": "D1008", "dis": "Ryhmatyotilat 4 op.", "co2": 0, "temp": 25.5, "occ": 0},
    "D1009": {"id": "D1009", "dis": "Ryhmatyotila 5 hlo", "co2": 0, "temp": 21.7, "occ": 0},
    "D1702": {"id": "D1702", "dis": "Sahkot.", "co2": 0, "temp": 22.9, "occ": 0},
    "A1702": {"id": "A1702", "dis": "Kerrosjakamo", "co2": 0, "temp": 23.0, "occ": 0}
}

# Space mapping: room number -> display name
SPACE_NAMES = {r["id"]: r["dis"] for r in SNAPSHOT_DATA.values()}


def air_quality_label(co2):
    if not co2:
        return "N/A"
    if co2 < CO2_GOOD:
        return "Good"
    if co2 < CO2_MEDIUM:
        return "Moderate"
    return "Poor"


def fetch_from_api():
    # Try the haystack endpoint first
    endpoints = [
        EB_BASE + "/haystack/read?filter=point+and+sensor+and+siteRef%3D%40Myllypuro_Campus",
        EB_BASE + "/organizations/" + EB_ORG + "/haystack/read?filter=point+and+sensor",
        EB_BASE + "/organizations/" + EB_ORG + "/sensors/current",
        EB_BASE + "/organizations/" + EB_ORG + "/assets/current_values",
    ]
    headers = {
        "Authorization": "Bearer " + EB_TOKEN,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    for url in endpoints:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    raw = resp.read().decode("utf-8")
                    data = json.loads(raw)
                    print("[CiC Twin] API success: " + url)
                    return data, url
        except urllib.error.HTTPError as e:
            print("[CiC Twin] HTTP " + str(e.code) + " for: " + url)
        except Exception as e:
            print("[CiC Twin] Error: " + str(e) + " for: " + url)
    return None, None


def parse_api_response(data):
    # Try to extract sensor readings from various response formats
    rooms = {}
    rows = []
    if isinstance(data, list):
        rows = data
    elif isinstance(data, dict):
        rows = data.get("rows", data.get("data", data.get("sensors", [])))

    for item in rows:
        if not isinstance(item, dict):
            continue
        space_ref = item.get("spaceRef", item.get("space_id", ""))
        if not space_ref:
            continue
        guid = space_ref.replace("r:", "")
        et   = item.get("eb_type", item.get("type", ""))
        val  = item.get("curVal", item.get("value", item.get("current_value")))
        if val is None:
            continue
        if isinstance(val, dict):
            val = val.get("val", val.get("value", 0))
        try:
            val = float(val)
        except Exception:
            continue
        if guid not in rooms:
            rooms[guid] = {"id": guid, "dis": SPACE_NAMES.get(guid, guid),
                           "co2": 0, "temp": 0, "occ": 0}
        if et in ("co2", "CO2"):
            rooms[guid]["co2"] = round(val, 1)
        elif et in ("temperature", "temp"):
            rooms[guid]["temp"] = round(val, 1)
        elif et in ("occupancy", "occ"):
            rooms[guid]["occ"] = int(val)
    return rooms if rooms else None


# Global state
_live_data = {}
_data_source = "snapshot"
_last_update = "Never"
_fetching = False


def do_fetch():
    global _live_data, _data_source, _last_update, _fetching
    _fetching = True
    print("[CiC Twin] Fetching live data...")
    raw, url = fetch_from_api()
    if raw:
        parsed = parse_api_response(raw)
        if parsed:
            _live_data = parsed
            _data_source = "live"
            import time
            _last_update = time.strftime("%H:%M:%S")
            print("[CiC Twin] Live data loaded: " + str(len(parsed)) + " rooms")
        else:
            _data_source = "snapshot (parse failed)"
            print("[CiC Twin] Could not parse response")
    else:
        _data_source = "snapshot (API unreachable)"
        print("[CiC Twin] All endpoints failed - using snapshot")
    _fetching = False


def get_room_data(room_id):
    if _live_data and room_id in _live_data:
        return _live_data[room_id]
    return SNAPSHOT_DATA.get(room_id)


def search_rooms(query):
    q = query.strip().lower()
    if not q:
        return []
    source = _live_data if _live_data else SNAPSHOT_DATA
    results = []
    for room in source.values():
        if q in room.get("id","").lower() or q in room.get("dis","").lower():
            results.append(room)
    return results


# --- PROPERTIES ---

class CiCSearchProps(bpy.types.PropertyGroup):
    query:         bpy.props.StringProperty(name="Search", default="")
    status:        bpy.props.StringProperty(default="")
    found_id:      bpy.props.StringProperty(default="")
    found_dis:     bpy.props.StringProperty(default="")
    found_co2:     bpy.props.StringProperty(default="")
    found_temp:    bpy.props.StringProperty(default="")
    found_occ:     bpy.props.StringProperty(default="")
    found_iaq:     bpy.props.StringProperty(default="")
    multi_results: bpy.props.StringProperty(default="")


# --- OPERATORS ---

class CIC_OT_SearchSensor(bpy.types.Operator):
    bl_idname = "cic.search_sensor"
    bl_label = "Look Up"
    bl_description = "Search for a room and show its sensor values"

    def execute(self, context):
        props = context.scene.cic_search
        results = search_rooms(props.query)

        for attr in ("found_id","found_dis","found_co2","found_temp",
                     "found_occ","found_iaq","multi_results","status"):
            setattr(props, attr, "")

        if not results:
            props.status = "No rooms found."
            return {"FINISHED"}

        if len(results) > 1:
            props.status = str(len(results)) + " rooms found - showing first."
            props.multi_results = ", ".join(r.get("dis", r.get("id","")) for r in results[:5])

        room = results[0]
        co2_val  = room.get("co2", 0)
        temp_val = room.get("temp", 0)
        occ_val  = room.get("occ", 0)

        props.found_id   = room.get("id", "-")
        props.found_dis  = room.get("dis", "-")
        props.found_co2  = str(co2_val) + " ppm" if co2_val else "N/A"
        props.found_temp = str(temp_val) + " C"  if temp_val else "N/A"
        props.found_occ  = str(occ_val) + " ppl"
        props.found_iaq  = air_quality_label(co2_val)

        if not props.status:
            props.status = "Found."
        return {"FINISHED"}


class CIC_OT_ClearSearch(bpy.types.Operator):
    bl_idname = "cic.clear_search"
    bl_label = "Clear"
    bl_description = "Clear search"

    def execute(self, context):
        props = context.scene.cic_search
        for attr in ("query","found_id","found_dis","found_co2","found_temp",
                     "found_occ","found_iaq","multi_results","status"):
            setattr(props, attr, "")
        return {"FINISHED"}


class CIC_OT_FetchLive(bpy.types.Operator):
    bl_idname = "cic.fetch_live"
    bl_label = "Fetch Live Data"
    bl_description = "Try to fetch latest sensor data from EmpathicBuilding API"

    def execute(self, context):
        global _fetching
        if _fetching:
            self.report({"INFO"}, "Already fetching...")
            return {"FINISHED"}
        t = threading.Thread(target=do_fetch, daemon=True)
        t.start()
        self.report({"INFO"}, "Fetching live data in background...")
        return {"FINISHED"}


# --- PANEL ---

class CIC_PT_SensorSearch(bpy.types.Panel):
    bl_label      = "Sensor Lookup"
    bl_idname     = "CIC_PT_sensor_search"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category   = "CiC Twin"

    def draw(self, context):
        layout = self.layout
        props  = context.scene.cic_search

        # Data source status
        src_box = layout.box()
        src_box.scale_y = 0.8
        src_box.label(text="Data: " + _data_source, icon="NETWORK_DRIVE")
        if _last_update != "Never":
            src_box.label(text="Updated: " + _last_update)
        layout.operator("cic.fetch_live", text="Refresh Live Data", icon="FILE_REFRESH")

        layout.separator()

        # Search
        box = layout.box()
        box.label(text="Search Room", icon="VIEWZOOM")
        row = box.row(align=True)
        row.prop(props, "query", text="")
        row.operator("cic.search_sensor", text="", icon="VIEWZOOM")
        box.operator("cic.clear_search", text="Clear", icon="X")

        if props.status:
            icon = "INFO" if "Found" in props.status else "ERROR"
            box.label(text=props.status, icon=icon)

        if props.multi_results:
            box.label(text="Also found:", icon="LINENUMBERS_ON")
            for name in props.multi_results.split(", "):
                box.label(text="  " + name)

        # Result
        if props.found_id:
            layout.separator()
            card = layout.box()
            card.label(text=props.found_dis, icon="HOME")
            card.label(text="Room: " + props.found_id)

            layout.separator()
            sensors = layout.box()
            sensors.label(text="Sensor Values", icon="DRIVER_TRANSFORM")
            iaq_icons = {"Good":"CHECKMARK","Moderate":"ERROR","Poor":"CANCEL"}
            iaq_icon  = iaq_icons.get(props.found_iaq, "QUESTION")
            row = sensors.row()
            row.label(text="CO2:  " + props.found_co2, icon="FORCE_WIND")
            row.label(text="IAQ: " + props.found_iaq, icon=iaq_icon)
            sensors.label(text="Temp: " + props.found_temp, icon="TEMP")
            sensors.label(text="Occ:  " + props.found_occ, icon="COMMUNITY")

        layout.separator()
        tip = layout.box()
        tip.scale_y = 0.7
        tip.label(text="Try: A1017, D1002, auditorio", icon="INFO")


CLASSES = [
    CiCSearchProps,
    CIC_OT_SearchSensor,
    CIC_OT_ClearSearch,
    CIC_OT_FetchLive,
    CIC_PT_SensorSearch,
]

def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.cic_search = bpy.props.PointerProperty(type=CiCSearchProps)
    # Auto-fetch on load
    t = threading.Thread(target=do_fetch, daemon=True)
    t.start()

def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.cic_search

if __name__ == "__main__":
    register()
