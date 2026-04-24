const express = require('express');
const multer  = require('multer');
const router  = express.Router();
const controller = require('../controllers/userController');

const upload = multer({ storage: multer.memoryStorage() });

// =======================
// 세션 관리 (보조 기능)
// =======================
router.get('/sessions',        controller.getSessions);
router.post('/sessions',       controller.createSession);
router.delete('/sessions/:id', controller.deleteSession);

// =======================
// 기존 핵심 기능
// =======================
router.post('/process', controller.processData);
router.get('/result',   controller.getResult);

// =======================
// AI — 사진 품질 검사
// =======================
router.post('/check/quality', upload.single('image'), controller.checkPhotoQuality);

// =======================
// AI — 체형 분석
// =======================
router.post('/analyze/body', upload.single('image'), controller.analyzeBody);

// =======================
// AI — 가상피팅
// =======================
router.post('/fitting/virtual', upload.fields([
  { name: 'human_img', maxCount: 1 },
  { name: 'garm_img',  maxCount: 1 },
]), controller.virtualFitting);

// =======================
// 관리자
// =======================
router.delete('/admin/reset', controller.resetDatabase);

module.exports = router;