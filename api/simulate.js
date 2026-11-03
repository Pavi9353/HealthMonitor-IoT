// Vercel Serverless Function — /api/simulate
// Returns simulated realistic health sensor data
// Used when no real ESP32 device is connected

export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json');

  // Simulate realistic fluctuating vitals
  const now = Date.now();
  const t = now / 3000;

  const heartRate  = +(70 + Math.sin(t * 0.7) * 8 + Math.random() * 3).toFixed(1);
  const spo2       = +(97 + Math.sin(t * 0.3) * 1.5 + Math.random() * 0.5).toFixed(0);
  const bodyTemp   = +(36.6 + Math.sin(t * 0.2) * 0.4 + Math.random() * 0.1).toFixed(1);

  const hrStatus   = heartRate < 60 ? 'Low (Bradycardia)' : heartRate > 100 ? 'High (Tachycardia)' : 'Normal';
  const spo2Status = spo2 < 90 ? 'Critical' : spo2 < 95 ? 'Low' : 'Normal';
  const tempStatus = bodyTemp > 38.5 ? 'Fever' : bodyTemp > 37.5 ? 'Slightly High' : bodyTemp < 36 ? 'Low' : 'Normal';
  const alertActive = hrStatus !== 'Normal' || spo2Status !== 'Normal' || tempStatus === 'Fever';

  res.status(200).json({
    heartRate,
    spo2: parseInt(spo2),
    bodyTemp,
    hrStatus,
    spo2Status,
    tempStatus,
    status: alertActive ? 'Alert' : 'Normal',
    alertActive,
    source: 'simulated',
    timestamp: now
  });
}
