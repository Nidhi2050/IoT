% ================================================================
%  REAL-TIME MULTI-DEVICE TEMPERATURE MONITORING – THRESHOLD 30°C
%  Updated with NEW CHANNEL + API KEYS + Correct Field Mapping
% ================================================================

% -------- Channel Info --------
readChannelID = 3178661;                 % NEW CHANNEL ID
readAPIKey    = 'XD5YM54WWPQVG20K';      % NEW READ KEY

% Field mapping (temperature only)
fields = [1, 2, 3];  
deviceNames = ["Temp_Device1", "Temp_Device2", "Temp_Device3"];

% Fan status field (as per new design)
fanField = 7;                             % Fan status is now field 7

% -------- Alerts Configuration --------
alertApiKey = "TAK+fuM5ft6GBy73QnU";       % NEW ALERT KEY
alertUrl = "https://api.thingspeak.com/alerts/send";

options = weboptions("HeaderFields", ...
            ["ThingSpeak-Alerts-API-Key", alertApiKey], ...
            "MediaType", "application/json");

% -------- Threshold --------
thresholdC = 30;

fprintf('\n=== REAL-TIME MULTI-DEVICE TEMPERATURE MONITORING ===\n');
fprintf('Monitoring Channel %d\n', readChannelID);
fprintf('Threshold = %.1f°C\n\n', thresholdC);

% -------- Read Latest Data for All 3 Devices --------
try
    [data, timeStamp] = thingSpeakRead(readChannelID, ...
                        "Fields", fields, ...
                        "NumPoints", 1, ...
                        "ReadKey", readAPIKey);

    if isempty(data)
        error("No data found.");
    end

    temps = data(1,:);   % row vector [T1 T2 T3]

catch ME
    fprintf('Error reading channel: %s\n', ME.message);
    return;
end

% -------- Display Readings --------
fprintf("Latest Readings (%s):\n", string(timeStamp));
for i = 1:length(fields)
    fprintf("  %s = %.2f°C\n", deviceNames(i), temps(i));
end

% -------- Check Threshold --------
exceedList = temps > thresholdC;

if ~any(exceedList)
    fprintf("\nAll temperatures are within safe range.\n");
    return;
end

% -------- Devices exceeding limit --------
exceedIdx = find(exceedList);
fprintf("\n⚠️ ALERT: Temperature threshold exceeded!\n");

alertDetails = "";
for i = exceedIdx
    fprintf("  - %s = %.2f°C (Above 30°C)\n", deviceNames(i), temps(i));

    % Create accurate per-device alert text
    alertDetails = alertDetails + sprintf("%s exceeded limit: %.2f°C\n", ...
                                          deviceNames(i), temps(i));
end

% -------- FAN CONTROL LOGIC --------
fanOn = 1;  
fanText = "ON";

fprintf("\nFan turned %s due to high temperature.\n", fanText);

% -------- SEND IMMEDIATE ALERT --------
mailSubject = sprintf("⚠️ High Temp Alert | Devices: %s | %s", ...
                       strjoin(deviceNames(exceedIdx), ", "), ...
                       string(timeStamp));

mailBody = sprintf( ...
    ['HIGH TEMPERATURE DETECTED!\n\n', ...
     'Timestamp: %s\n\n', ...
     'Devices Above Threshold:\n%s\n', ...
     'Threshold: %.1f°C\n\n', ...
     'Fan Action: %s\n\n', ...
     'This is an automated IoT Vaccine-Guard Alert.'], ...
     string(timeStamp), alertDetails, thresholdC, fanText);

try
    bodyStruct = struct('body', mailBody, 'subject', mailSubject);
    webwrite(alertUrl, bodyStruct, options);
    fprintf("\nEmail alert sent successfully.\n");
catch ME
    fprintf("\nError sending alert: %s\n", ME.message);
end

fprintf("\n=== Monitoring Completed ===\n");
