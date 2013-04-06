struct config_t
{
  int stepsPerRevolution;
  float stepsPerMM;
  int hanger_l; //mm
  int top_margin; //mm
  int side_margin; //mm
  float motor_dist_mm; //mm
  float width; //mm
  float height; //mm
  byte id;
  float gondola_width; //mm
  int default_pwm;
  int lowpower_pwm;
  int home_pwm_high;
  int home_pwm_low;
  int home_speed;
  int maxSpeed;
} 
config;
