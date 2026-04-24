// backend/services/aiService.js
// Python AI 서비스(FastAPI)와 통신하는 클라이언트

const FormData = require('form-data');
const fetch = (...args) => import('node-fetch').then(({ default: f }) => f(...args));

const AI_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000';

// ── 사진 품질 검사 ────────────────────────────────────────────────────────────

exports.checkPhotoQuality = async (imageBuffer) => {
  const form = new FormData();
  form.append('image', imageBuffer, { filename: 'photo.jpg', contentType: 'image/jpeg' });

  const res = await fetch(`${AI_URL}/check/quality`, { method: 'POST', body: form });
  if (!res.ok) throw new Error(`품질 검사 실패: ${await res.text()}`);
  return res.json();
};

// ── 체형 분석 ─────────────────────────────────────────────────────────────────

exports.analyzeBody = async (imageBuffer, height, weight) => {
  const form = new FormData();
  form.append('image', imageBuffer, { filename: 'photo.jpg', contentType: 'image/jpeg' });
  form.append('height', String(height));
  form.append('weight', String(weight));

  const res = await fetch(`${AI_URL}/analyze/body`, { method: 'POST', body: form });
  if (!res.ok) throw new Error(`체형 분석 실패: ${await res.text()}`);
  return res.json();
};

// ── 가상피팅 ──────────────────────────────────────────────────────────────────

exports.virtualFitting = async (humanImgBuffer, garmImgBuffer, garmentDesc = '') => {
  const form = new FormData();
  form.append('human_img', humanImgBuffer, { filename: 'human.jpg', contentType: 'image/jpeg' });
  form.append('garm_img', garmImgBuffer,   { filename: 'outfit.jpg', contentType: 'image/jpeg' });
  form.append('garment_desc', garmentDesc);

  const res = await fetch(`${AI_URL}/fitting/virtual`, { method: 'POST', body: form });
  if (!res.ok) throw new Error(`가상피팅 실패: ${await res.text()}`);
  return res.json();
};
