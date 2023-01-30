from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import scrolledtext
from tkinter import ttk
from PIL import Image, ImageTk
from scraper import Scraper
from bs4 import BeautifulSoup
import threading, os, openpyxl, time, json


# App Class
class App:
	def __init__(self):
		threading.Thread.__init__(self)
		
		# Base options
		self.title = "Proteinatlas Scraper"
		self.guiWidth = 650
		self.guiHeight = 260
		self.textColor = "white"
		self.guiBaseColor = '#1e1f21'
		self.guiSecondColor = "#00b84c"
		self.root = None
		self.max_threads = 2
		self.version = "22.06.30"
		self.task_run = False
		self.output_headers = ["Speciem","Accession","Protein Description (GN=)","Full Protein Description","Number of Peptides","Link","Tissue specificity","Tissue expression cluster","specific","status"]
		self.input_method = None
		self.max_cache_days = 30
		self.output_save_every = 10

	def clear(self):
		print("clear(): Called")
		for widget in self.rootFrame.winfo_children(): widget.destroy()
	
	def draw(self):
		global import_filename_label_string, status_label_string, pb, button_start, button_stop, entry_max_threads, status_label
		print("draw(): Called")

		def selectInputExcelFile():			
			print("draw(): selectInputExcelFile(): Called")
			fl = filedialog.askopenfilename(filetypes =[('Excel', '*.xlsx')], title="Choose an excel file")
			if fl:
				self.input_method = {"type":"excel", "path":fl}
				import_filename_label_string.set("Excel method selected: "+fl)
				
		def selectInputHTMLFile():			
			print("draw(): selectInputHTMLFile(): Called")
			fl = filedialog.askopenfilenames(filetypes =[('Html', '*.html')], title='Choose html files')
			if fl:
				self.input_method = {"type":"html", "path":fl}
				import_filename_label_string.set("HTML method selected: {0} file(s)".format(len(fl)))
			
		def startTask():
			print("draw(): scrap(): Called")
			
			if self.input_method:
				
				# Apply threads
				try:
					threads_tmp = int(entry_max_threads.get())
					if threads_tmp <= 5 and threads_tmp > 0:
						
						# Ui update
						status_label_string.set("Starting...")
						status_label.configure(fg=self.guiSecondColor)
						button_start.pack_forget()
						button_stop.pack()
						
						# Load data & Task set
						input_records = []
						if self.input_method["type"] == "excel":
							wb_inp = openpyxl.load_workbook(self.input_method["path"])
							sheet_inp = wb_inp.active
							for row in sheet_inp.iter_rows(min_row=1, min_col=1):
								input_records.append({
									"speciem":row[0].value,
									"accesion":row[1].value,
									"protein_description":row[2].value,
									"protein_full_description":"",
									"num_of_peptides":row[3].value,
								})
							wb_inp.close()
						
						if self.input_method["type"] == "html":
							for html_file in self.input_method["path"]:
								with open(html_file, 'r') as file:
									soup = BeautifulSoup(file.read(), "html.parser")
									trs = soup.find(id="top-proteins").find("tbody").find_all("tr")
									for tr in trs:
										tds = tr.find_all("td")
										
										html_filename = html_file.split("/")[-1]
										html_filename = html_filename.split(".")[0]
										
										protein_description = tds[1].text
										if protein_description.find("GN=") >= 0:
											protein_description = protein_description[protein_description.find("GN=")+3:]
											protein_description = protein_description[:protein_description.find(" ")]
										else:
											protein_description = ""
										
										input_records.append({
											"speciem":html_filename,
											"accesion":tds[0].text,
											"protein_description":protein_description,
											"protein_full_description":tds[1].text,
											"num_of_peptides":tds[2].text,
										})
						
						self.max_threads = threads_tmp
						self.task_run = True
						threading.Thread(target=self.scrap, args=(input_records,)).start()
					else:
						messagebox.showerror("Settings Error","Threads cannot be more than 5.")
					
				except (TypeError, ValueError) as e:
					print(e)
					messagebox.showerror("Task Error","Threads must be a number.")
			else:
				messagebox.showerror("Task Error","Please select an input file first!")
				
		def stopTask():
			status_label.configure(fg=self.textColor)
			self.task_run = False
			button_stop.pack_forget()
			button_start.pack(side="right")
			
		# Init main Window
		self.root = Tk()
		self.root.geometry("{0}x{1}".format(self.guiWidth,self.guiHeight))
		self.root.title(self.title)
		self.root.configure(background=self.guiBaseColor, padx=10, pady=10)
		self.root.resizable(False, False)
		
		# Init Left side frame - File selection
		leftFrame = Frame(self.root, background=self.guiBaseColor)
		leftFrame.grid(row=0, column=0, padx=20, pady=10)

		import_from_excel_btn_photo = PhotoImage(file='assets/import_from_excel.png')
		import_form_excel_btn = Button(leftFrame, image=import_from_excel_btn_photo, command=selectInputExcelFile, bd=0, highlightthickness=0, borderwidth=0, activebackground=self.guiBaseColor, bg=self.guiBaseColor)
		import_form_excel_btn.pack(pady=10)
		
		import_from_html_btn_photo = PhotoImage(file='assets/import_from_html.png')
		import_form_html_btn = Button(leftFrame, image=import_from_html_btn_photo, command=selectInputHTMLFile, bd=0, highlightthickness=0, borderwidth=0, activebackground=self.guiBaseColor, bg=self.guiBaseColor)
		import_form_html_btn.pack(pady=10)
		
		# Init right side frame - Progress bar & status
		rightFrame = Frame(self.root, background=self.guiBaseColor)
		rightFrame.grid(row=0, column=1, padx=10, pady=10)
		
		import_filename_label_string = StringVar()
		import_filename_label_string.set("Selected file: No file selected yet.")
		import_filename_label = Label(rightFrame, textvariable=import_filename_label_string, background=self.guiBaseColor, fg=self.textColor, borderwidth=0, wraplength=self.guiWidth-180)
		import_filename_label.pack(pady=5)
		
		pb = ttk.Progressbar(rightFrame, orient='horizontal', mode='determinate', length=(self.guiWidth-180))
		pb.pack()
		
		status_label_string = StringVar()
		status_label = Label(rightFrame, textvariable=status_label_string, background=self.guiBaseColor, fg=self.textColor, borderwidth=0)
		status_label.pack(pady=5)
		status_label_string.set("Task: Not started.")
		
		# Bottom Frame - Scrap button
		bottomFrame = Frame(self.root, background=self.guiBaseColor)
		bottomFrame.grid(row=1, column=1)

		label_threads = Label(bottomFrame, text="Number of threads", background=self.guiBaseColor, fg=self.textColor, borderwidth=0)
		label_threads.pack(side="left", padx=4)
		entry_max_threads = Entry(bottomFrame, width=5, borderwidth=0, background=self.guiBaseColor,fg=self.textColor)
		entry_max_threads.insert(0, self.max_threads)
		entry_max_threads.pack(side="left", padx=5)

		button_start = Button(bottomFrame, text="Scrap!", command=startTask, borderwidth=0, background=self.guiBaseColor,fg=self.textColor)
		button_start.pack(side="right", padx=10)
		
		button_stop = Button(bottomFrame, text="Cancel", command=stopTask, borderwidth=0, background=self.guiBaseColor,fg=self.textColor)

		# Begin lifecycle - waiting for events
		self.root.mainloop()
		
	def scrap(self, input_records):
		
		# create output file
		output_filename = "output.xlsx"
		if os.path.isfile(output_filename): messagebox.showwarning("File Warning","Output file already exists! Will append new records.")
		wb_out = openpyxl.Workbook() 
		ws_out = wb_out.active
		ws_out.append(self.output_headers)

		# Set a worker pool
		worker_pool = []

		# Load cache file
		if os.path.isfile('cache.json'):
			with open('cache.json') as json_file: cached_data = json.load(json_file)
		else:
			cached_data = {}

		# read terms from input file
		records_written = 0
		for input_record in input_records:

			if not self.task_run:
				status_label_string.set("[{0:.1f}%] {1} / {2} Scraping -> Canceled".format(pb["value"], records_written, len(input_records)))
				messagebox.showinfo("Task Info","Canceled!")
				return
				
			# Check in cache
			try:
				cached_record = cached_data[input_record["protein_description"]]
				days_passed = (int(time.time()) - cached_record["timestamp"]) / 86400
				if days_passed >= self.max_cache_days: raise KeyError("Renew cached record")

				records_written+=1
				pb["value"] = (records_written * 100) / len(input_records)
				status_label_string.set("[{0:.1f}%] {1} / {2} Scraping -> Cached {3}".format(pb["value"], records_written, len(input_records), input_record["protein_description"]))
				print("draw(): scrap(): [{0:.1f}%] {1} / {2} Scraping -> Cached {3}".format(pb["value"], records_written, len(input_records), input_record["protein_description"]))
				ws_out.append([input_record["speciem"], input_record["accesion"], input_record["protein_description"], input_record["protein_full_description"], input_record["num_of_peptides"], cached_record["link"], cached_record["tissue_specificity"], cached_record["tissue_expression_cluster"], cached_record["specific"], "1"])
				if records_written%self.output_save_every == 0: wb_out.save(filename=output_filename)
				continue
			except (IndexError, KeyError): pass

			# Wait until there is space in pool
			while len(worker_pool) >= self.max_threads:
				time.sleep(0.3)
				for worker in worker_pool:
					if not worker.is_alive():
						result = worker.result
						records_written+=1
						pb["value"] = (records_written * 100) / len(input_records)
						status_label_string.set("[{0:.1f}%] {1} / {2} Scraping -> {3}".format(pb["value"], records_written, len(input_records), input_record["protein_description"]))
						print("draw(): scrap(): [{0:.1f}%] {1} / {2} Scraping -> {3}".format(pb["value"], records_written, len(input_records), input_record["protein_description"]))
						
						if result:								
							ws_out.append([worker.input_record["speciem"], worker.input_record["accesion"], worker.input_record["protein_description"], worker.input_record["protein_full_description"], worker.input_record["num_of_peptides"], result["link"], result["tissue_specificity"], result["tissue_expression_cluster"], result["specific"], "1"])
							
							# Append to cache
							cached_data[worker.input_record["protein_description"]] = result

						else:
							
							ws_out.append([worker.input_record["speciem"], worker.input_record["accesion"], worker.input_record["protein_description"], worker.input_record["protein_full_description"], worker.input_record["num_of_peptides"], "", "", "", "", "0"])

						if records_written%self.output_save_every == 0: wb_out.save(filename=output_filename)
						worker_pool.remove(worker)
						break
			
			# start next worker
			myWorker = Scraper(input_record)
			myWorker.daemon = True
			myWorker.start()
			worker_pool.append(myWorker)
			
		# wait until last threads ends
		for worker in worker_pool:
			worker.join()
			result = worker.result
			records_written+=1
			pb["value"] = (records_written * 100) / len(input_records)
			status_label_string.set("[{0:.1f}%] {1} / {2} Scraping -> {3}".format(pb["value"], records_written, len(input_records), input_record["protein_description"]))
			print("draw(): scrap(): [{0:.1f}%] {1} / {2} Scraping -> {3}".format(pb["value"], records_written, len(input_records), input_record["protein_description"]))
			
			if result:								
				ws_out.append([input_record["speciem"], input_record["accesion"], input_record["protein_description"], input_record["protein_full_description"], input_record["num_of_peptides"], result["link"], result["tissue_specificity"], result["tissue_expression_cluster"], result["specific"], "1"])
			else:
				ws_out.append([input_record["speciem"], input_record["accesion"], input_record["protein_description"], input_record["protein_full_description"], input_record["num_of_peptides"], "", "", "", "", "0"])

		# Save & close excel
		wb_out.save(filename=output_filename)
		wb_out.close()
		
		# Save cache
		with open('cache.json', 'w') as outfile: json.dump(cached_data, outfile)
		
		self.task_run = False
		button_stop.pack_forget()
		button_start.pack(side="right")
		messagebox.showinfo("Info","Completed!")

# run
App().draw()
