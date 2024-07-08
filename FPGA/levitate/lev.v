module controller (
    input clk,
    input wire reset,
    input wire [11:0] sensor,
    output wire [11:0] pwm_output
);

    // Parameters for PID controller
    parameter signed [11:0] Kp = 12'd1; // Proportional gain
    parameter signed [11:0] Ki = 12'd1; // Integral gain
    parameter signed [11:0] Kd = 12'd1; // Derivative gain
    parameter signed [11:0] limMax = 12'd255 // Max limit of integrator
    parameter signed [11:0] limMin = 12'd0 // Max limit of integrator
    parameter signed [11:0] T = 12'd1;
    parameter signed [11:0] tau = 8'd1;
    localparam WAIT_TIME = 13500000; //sampling time 

    // Internal registers for PID calculations
    reg signed [11:0] setpoint = 12'd2048; // Desired position (midpoint for 12-bit ADC)
    reg signed [11:0] error;
    reg signed [23:0] integrator;
    reg signed [11:0] derivative;
    reg signed [23:0] control_output;
    reg signed [11:0] prev_error;
    reg signed [11:0] prev_sensor
    reg signed [11:0] limMaxInt;
    reg signed [11:0] limMinInt;
    reg [23:0] clockCounter = 0;

    always @(posedge clk or posedge reset) begin
        clockCounter <= clockCounter + 1;
        if (reset) begin
            // Reset all registers (may be possibleto use "=" to speed this up)
            error <= 12'd0;
            integrator <= 12'd0;
            derivative <= 12'd0;
            control_output <= 12'd0;
            prev_error <= 12'd0;
            proportional <= 12'd0;
            limMaxInt <= 12'd0;
            limMinInt <= 12'd0;
            prev_sensor <= 12'd0;
            T <= 12'd0;
            tau <= 12'd0; 
        end
            
        if (clockCounter == WAIT_TIME) begin
            clockCounter <= 0; //reset counter to 0
            // Error calculation
            error <= setpoint - sensor;

            //Proportional
            proportional <=  Kp * error;

            // Integrator term calculation
            integrator <= integrator + (Ki * T * (error + prev_error));

            //Compute integrator limits

            if (limMax > proportional) begin
                limMaxInt <= limMax - proportional;
            end else begin
                limMaxInt <= 12'd0;
            end

            if (limMin < proportional) begin
                limMinInt <= limMin - proportional;
            end 
            
            else begin
                limMinInt <= 12'd0;
            end

            // Clamp integrator 

            if(integrator > limMaxInt)begin
                integrator <= limMaxInt;
            end 
            
            else if (integrator < limMinInt)begin
                integrator <= limMinInt;
            end

            // Derivative term calculation
            derivative <= (Kd * (sensor - prev_sensor) + (tau - T) * derivative) / (tau + T)

            // PID control calculation
            control_output <= proportional + integrator + derivative;

            if (control_output > limMax)begin
                control_output <= limMax
            end

            else if (control_output < limMin)begin
                control_output <= limMin
            end

            // Update previous error and sensor data
            prev_error <= error;
            prev_sensor <= sensor;

        end
    end

    // PWM output generation (example logic)
    assign pwm_output = (control_output > 0) ? control_output : 12'd0;

endmodule