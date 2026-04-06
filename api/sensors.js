// Vercel serverless function: /api/sensors
// Fetches live haystack data from EmpathicBuilding API and returns
// it mapped to the same room structure used by the search page.

const SPACE_MAPPING = [
  {"space_guid":"2yMDhecf15ff0Qukb9SbDN","space_number":"D1002","space_name":"Auditorio 200 paikkaa"},
  {"space_guid":"2yMDhecf15ff0Qukb9SbDr","space_number":"C1504","space_name":"Yleisöaula"},
  {"space_guid":"2yMDhecf15ff0Qukb9SbDh","space_number":"D1506","space_name":"Megora (kahvio)"},
  {"space_guid":"2yMDhecf15ff0Qukb9SbDY","space_number":"D1505","space_name":"Kirjasto, lehdet"},
  {"space_guid":"2yMDhecf15ff0Qukb9Sb8H","space_number":"C1502","space_name":"Avoin opiskelu"},
  {"space_guid":"2yMDhecf15ff0Qukb9SbAi","space_number":"C1002","space_name":"Info"},
  {"space_guid":"2w2pefRQvF7h8LEseDEATK","space_number":"B1505","space_name":"Innovaatiotilat"},
  {"space_guid":"2w2pefRQvF7h8LEseDEAHN","space_number":"C1016","space_name":"WC etutila/yl."},
  {"space_guid":"2w2pefRQvF7h8LEseDEAHQ","space_number":"C1503","space_name":"Avoin opiskelu"},
  {"space_guid":"1eq_WFYi92sOpYQ6IPK5GT","space_number":"A1017","space_name":"Ruokailutilat 6 hlo"},
  {"space_guid":"3REiYV$k585PAj4vH_l$yJ","space_number":"A1018","space_name":"Ruokailutilat 6 hlo"},
  {"space_guid":"2VBKoKYCrFHA7YD2Yz5YHt","space_number":"A1504","space_name":"Kaytava"},
  {"space_guid":"0n4WXPYzTAUPHDjl_ZJc4c","space_number":"A1013","space_name":"Ruokailutilat 25 hlo"},
  {"space_guid":"0n4WXPYzTAUPHDjl_ZJcvz","space_number":"A1014","space_name":"Ruokailutilat 30 hlo"},
  {"space_guid":"3REiYV$k585PAj4vH_l$xJ","space_number":"A1019","space_name":"Ruokailutilat 6 hlo"},
  {"space_guid":"0n4WXPYzTAUPHDjl_ZJc79","space_number":"A1015","space_name":"Ruokailutilat 6 hlo"},
  {"space_guid":"3REiYV$k585PAj4vH_l$cd","space_number":"A1016","space_name":"Ruokailutilat"},
  {"space_guid":"3VTYFK8vD6zQrOpleLa9QL","space_number":"B1001","space_name":"Kuntosali"},
  {"space_guid":"3VTYFK8vD6zQrOpleLa9Rz","space_number":"D1001","space_name":"Luentosali 120 paikkaa"},
  {"space_guid":"1DLz7Pej9EBA1hiXfC1nVw","space_number":"A1001","space_name":"Optikkomyymala NT"},
  {"space_guid":"1jj4UJ9Z51Vf5Aif_RU6nY","space_number":"A1002","space_name":"Optikkomyymala HIONTA"},
  {"space_guid":"2w2pefRQvF7h8LEseDEAs","space_number":"A1003","space_name":"Optikkomyymala"},
  {"space_guid":"0aCMxuq4v0UuWviG7ktEyv","space_number":"A1004","space_name":"Aistihuone"},
  {"space_guid":"2QBNHzWJLAYwHk1QrynqYa","space_number":"B1101","space_name":"Jalkaterapia 2 op"},
  {"space_guid":"2QBNHzWJLAYwHk1QrynqYs","space_number":"B1102","space_name":"Jalkaterapia 2 op"},
  {"space_guid":"2QBNHzWJLAYwHk1QrynqYx","space_number":"B1103","space_name":"Jalkaterapia 4 op"},
  {"space_guid":"2QBNHzWJLAYwHk1QrynqjU","space_number":"B1104","space_name":"Jalkaterapia 2 op"},
  {"space_guid":"2QBNHzWJLAYwHk1QrynqjZ","space_number":"B1105","space_name":"Jalkaterapia 2 op"},
  {"space_guid":"2QBNHzWJLAYwHk1Qrynqje","space_number":"B1106","space_name":"Jalkaterapia 2 op"},
  {"space_guid":"2QBNHzWJLAYwHk1Qrynqjz","space_number":"B1107","space_name":"Jalkaterapia 4 op"},
  {"space_guid":"1BZFaUBxbCZQkZ$3PjR_ic","space_number":"B1201","space_name":"Suun hoidon opetusklinikka RTG"},
  {"space_guid":"2w2pefRQvF7h8LEseDEA2t","space_number":"A1020","space_name":"Liikelaboratorio 30 op"},
  {"space_guid":"1ZghLtgbj2$RBcT74OM5uL","space_number":"C1101","space_name":"Kotikulma OH"},
  {"space_guid":"2QBNHzWJLAYwHk1Qrynqmj","space_number":"C1201","space_name":"Positia terapia 2 op"},
  {"space_guid":"2QBNHzWJLAYwHk1Qrynqmn","space_number":"C1202","space_name":"Positia terapia 2 op"},
  {"space_guid":"2QBNHzWJLAYwHk1Qrynqp5","space_number":"C1203","space_name":"Positia terapia 2 op"},
  {"space_guid":"2QBNHzWJLAYwHk1QrynqpB","space_number":"C1204","space_name":"Positia terapia 2 op"},
  {"space_guid":"0tJDAC8J94BApUpHeb5PSl","space_number":"C1205","space_name":"Positian asiakastilat 6 op"},
  {"space_guid":"2c9k63Vdz5Gxe1vA9WG9f$","space_number":"D1101","space_name":"Demoluokka 100 op"},
  {"space_guid":"2w2pefRQvF7h8LEseDEAHg","space_number":"A1505","space_name":"Kaytava"},
  {"space_guid":"2yMDhecf15ff0Qukb9SbDr","space_number":"C1504","space_name":"Yleisöaula"},
  {"space_guid":"0u5psq1b94ZBnOoQFbHWM9","space_number":"C1501","space_name":"Avoin opiskelu"},
  {"space_guid":"2yMDhecf15ff0Qukb9SbDN","space_number":"D1002","space_name":"Auditorio 200 paikkaa"},
  {"space_guid":"2yMDhecf15ff0Qukb9SbDh","space_number":"D1506","space_name":"Megora kahvio"},
  {"space_guid":"27GLV1F0X8jAWU3Z5BzTKG","space_number":"D1003","space_name":"Iso auditorio 275 paikkaa"},
  {"space_guid":"2w2pefRQvF7h8LEseDEAEa","space_number":"B1301","space_name":"Suun hoidon opetusklinikka 50 op"}
];

const EB_API = "https://eu-api.empathicbuilding.com/v1";
const TOKEN  = process.env.EB_TOKEN || "8053a0ed-3584-40a6-911f-dbfc34a45dc1";

function buildGuidMap() {
  const m = {};
  for (const s of SPACE_MAPPING) {
    m[s.space_guid] = { room_number: s.space_number, dis: s.space_name };
  }
  return m;
}

export default async function handler(req, res) {
  // CORS so browser can call this from any origin
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET");

  try {
    const response = await fetch(`${EB_API}/haystack/read?filter=point+and+sensor+and+siteRef%3D%40Myllypuro_Campus`, {
      headers: {
        Authorization: `Bearer ${TOKEN}`,
        Accept: "application/json",
      },
    });

    if (!response.ok) {
      return res.status(502).json({ error: "EB API error", status: response.status });
    }

    const data = await response.json();
    const rows = data.rows || data;
    const guidMap = buildGuidMap();

    const rooms = {};
    for (const item of rows) {
      if (!item.spaceRef || item.curVal === undefined) continue;
      const guid = (item.spaceRef.val || item.spaceRef || "").replace("r:", "");
      const et = item.eb_type;
      if (!rooms[guid]) {
        const info = guidMap[guid] || {};
        rooms[guid] = {
          id: "r:" + guid,
          room_number: info.room_number || guid.slice(0, 8),
          dis: info.dis || item.dis_space || guid,
          floor: "Ground Floor",
          co2: null, temp: null, occ: null, humid: null,
        };
      }
      const val = typeof item.curVal === "object" ? item.curVal.val : item.curVal;
      if (et === "co2"         && rooms[guid].co2   === null) rooms[guid].co2   = Math.round(val * 10) / 10;
      if (et === "temperature" && rooms[guid].temp  === null) rooms[guid].temp  = Math.round(val * 10) / 10;
      if (et === "occupancy"   && rooms[guid].occ   === null) rooms[guid].occ   = Math.round(val);
      if (et === "humidity"    && rooms[guid].humid === null) rooms[guid].humid = Math.round(val * 10) / 10;
    }

    res.setHeader("Cache-Control", "s-maxage=60, stale-while-revalidate=30");
    return res.status(200).json({
      rooms: Object.values(rooms),
      fetched_at: new Date().toISOString(),
    });

  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
}

