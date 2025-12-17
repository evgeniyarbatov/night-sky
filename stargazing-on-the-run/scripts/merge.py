import sys	
import glob
import os
import re
import shutil

from PIL import Image

def main(
	gpx_dir,
	screenshot_dir,
	maps_dir,
	output_dir,
):
	gpx_files = glob.glob(
		os.path.join(gpx_dir, '*.gpx'),
	)
	for gpx_file in gpx_files:
		filename = os.path.splitext(os.path.basename(gpx_file))[0]    

		output_path = f"{output_dir}/{filename}"
		os.makedirs(output_path)

		map_files = glob.glob(os.path.join(f"{maps_dir}/{filename}", "*.png"))
		screenshot_files = glob.glob(os.path.join(f"{screenshot_dir}/{filename}", "*.jpeg"))

		for map_file in map_files:
			timestamp = os.path.splitext(os.path.basename(map_file))[0] 
			screenshot_file = [s for s in screenshot_files if timestamp in s][0]

			with open(screenshot_file, 'rb') as s, open(map_file, 'rb') as m:
				im1 = Image.open(s)
				im2 = Image.open(m)

				max_height = im1.height * 0.25
				if im2.height > max_height:
					scale = max_height / im2.height
					im2 = im2.resize((int(im2.width * scale), int(im2.height * scale)))

				position = ((im1.width - im2.width), (im1.height - im2.height))
				im1.paste(
					im2, 
					position,
				)

				im1.save(
					f'{output_path}/{timestamp}.png',
					optimize=True,
					quality=95
				)

				im1.close()
				im2.close()

				del im1
				del im2

if __name__ == "__main__":
    main(*sys.argv[1:])