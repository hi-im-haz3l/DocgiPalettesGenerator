import cv2
import numpy as np
from sklearn.cluster import KMeans
import imutils
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cmc
from colormath.color_objects import sRGBColor, LabColor, HSLColor
import json

clusters = 5
errors = []
primary_delta_e = 559
accent_delta_e = 365

def calculate_delta_e(color1, color2):
    color1_rgb = sRGBColor(color1[0], color1[1], color1[2])
    color2_rgb = sRGBColor(color2[0], color2[1], color2[2])

    color1_lab = convert_color(color1_rgb, LabColor)
    color2_lab = convert_color(color2_rgb, LabColor)

    return delta_e_cmc(color1_lab, color2_lab)

def get_neighbour_color(color):
    rgb_color = sRGBColor(color[0], color[1], color[2])
    hsl_color = convert_color(rgb_color, HSLColor)
    neighbour_color = [hsl_color.hsl_h, hsl_color.hsl_s, 0]
    
    if (hsl_color.hsl_l > 127):
        neighbour_color[2] = hsl_color.hsl_l - 5

    else:
        neighbour_color[2] = hsl_color.hsl_l + 7

    color2_rgb = HSLColor(neighbour_color[0], neighbour_color[1], neighbour_color[2])
    color2_lab = convert_color(color2_rgb, sRGBColor)
    return [round(color2_lab.rgb_r), round(color2_lab.rgb_g), round(color2_lab.rgb_b)]

def stringify_list(list):
    return ', '.join(str(x) for x in list)

with open('./manifest.json', 'r', encoding="utf8") as f:
    data = json.load(f)

for idx, book in enumerate(data):
    image_path = book['image_paths'][0]
    try:
        img = cv2.imread(image_path)

        org_img = img.copy()
        img = imutils.resize(img,height=200)
        flat_img = np.reshape(img,(-1,3))

        kmeans = KMeans(n_clusters=clusters,random_state=0)
        kmeans.fit(flat_img)

        dominant_colors = np.array(kmeans.cluster_centers_,dtype='uint')

        percentages = (np.unique(kmeans.labels_,return_counts=True)[1])/flat_img.shape[0]
        p_and_c = zip(percentages,dominant_colors)
        p_and_c = sorted(p_and_c, key=lambda x: x[0], reverse=True)

        colors = []

        for i in range(clusters):
            bgr_color = p_and_c[i][1]

            rgb_color = bgr_color[...,::-1]
            rgb_color = rgb_color.tolist()

            colors.append(rgb_color)
        
        extended_clusters = clusters
        delta_e = 0
        smallest_delta_e = 9000
        largest_delta_e = 0
        closest_colors = [0, 0, 0]
        farthest_colors = [0, 0, 0]

        for i in range(1, extended_clusters):
            delta_e = calculate_delta_e(colors[0], colors[i])

            if (delta_e > largest_delta_e):
                farthest_colors = colors[i]
                largest_delta_e = delta_e

            if (delta_e < smallest_delta_e):
                closest_colors = colors[i]
                smallest_delta_e = delta_e

            if (i + 1 == clusters):
                if(largest_delta_e < primary_delta_e):
                    default_color = [[255, 255, 255], [0, 0, 0]]
                    extended_clusters += 2

                if (smallest_delta_e > accent_delta_e):
                    closest_colors = get_neighbour_color(colors[0])

        data[idx]['color_palette'] = {
            'gradient': f"linear-gradient(315deg,rgb({stringify_list(colors[0])}) 0%,rgb({stringify_list(closest_colors)}) 100%)",
            'accent': f"rgb({stringify_list(farthest_colors)})"
        }

        print(f"Progress: {idx+1}/{len(data)}")

    except:
        errors.append(image_path)
        print("Failed to read image!")
        
        data[idx]['color_palette'] = {
            'gradient': "linear-gradient(315deg,rgba(142, 158, 171) 0%,rgba(189, 195, 199) 100%)",
            'accent': "rgb(255, 255, 255)"
        }

print(f"Stats: {len(data) - len(errors)} completed, {len(errors)} errors")

for i, error in enumerate(errors):
    print(f"Error ({i}): {error}")

with open("./manifest.json", "w", encoding="utf8") as outfile:
    json.dump(data, outfile)