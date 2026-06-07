function cfg = read_json_config(filename)
%READ_JSON_CONFIG Read a JSON file into a MATLAB struct.
    if ~isfile(filename)
        error('Config file not found: %s', filename);
    end
    txt = fileread(filename);
    cfg = jsondecode(txt);
end
