// Tab S7 (gts7lwifi / Halium): no GPU/VAAPI video decode, force YouTube onto H.264
// (much cheaper to software-decode than AV1/VP9). Cap to 60fps for 120Hz panel.
pref("media.av1.enabled", false);
pref("media.mediasource.vp9.enabled", false);
pref("media.webm.enabled", false);
pref("layout.frame_rate", 60);
