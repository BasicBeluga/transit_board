def dict_2_palette(in_dict):
    # name, foreground, background, mono, foreground_high, background_high
    out_list = []
    out_list.append(in_dict['name'])
    out_list.append(in_dict['foreground'])
    out_list.append(in_dict['background'])
    if 'mono' in in_dict:
        out_list.append(in_dict['mono'])
        if 'foreground_high' in in_dict:
            out_list.append(in_dict['foreground_high'])
            if 'background_high' in in_dict:
                out_list.append(in_dict['background_high'])

    return tuple(out_list)