import tkinter as tk
import random
import time

class BatchProcess:
    def __init__(self, root):
        # variables
        self.id_counter = 0
        self.process_list = []  # New processes, not ready
        self.ready_list = []
        self.in_execution = []
        self.blocked_list = []

        self.current_timer = None
        self.process = None
        self.is_paused = False

        # Window configuration
        self.root = root
        self.root.title("Practica 2")
        self.root.geometry("850x405")
        self.root.resizable(False, False)
        self.create_widgets()

        self.root.bind('e', self.stop_process)
        self.root.bind('i', self.interrupt_process)
        self.root.bind('p', self.pause_process)
        self.root.bind('c', self.continue_process)
    
    def create_widgets(self):
        self.create_header_frame()
        self.create_execution_frame()
        self.create_process_management_frame()
    
    ###########################################################################
    ####################### Functions to create widgets #######################
    ###########################################################################
    def create_header_frame(self):
        self.header_frame = tk.Frame(self.root, bd=2, relief="groove")
        self.header_frame.columnconfigure(0, weight=1)
        self.header_frame.columnconfigure(1, weight=1)
        self.header_frame.columnconfigure(2, weight=1)
        self.header_frame.columnconfigure(3, weight=1)

        self.batch_count = 0  # Global Counter for batch
        self.start = tk.Button(self.header_frame, text="Iniciar Simulación", font=("Arial", 10), height=2, width=15, command=self.start_simulation)
        self.start.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.remaining_batch = tk.Label(self.header_frame, text="Lotes restantes:\n0", font=("Arial", 15))
        self.remaining_batch.grid(row=0, column=2, padx=15, pady=10, sticky="E")

        # Global Timer inside header
        self.label = tk.Label(self.header_frame, text="00:00:00", font=("Arial", 20))
        self.elapsed_time = 0
        self.global_timer()
        self.label.grid(row=0, column=3, padx=15, pady=10, sticky="E")

        self.header_frame.pack(fill="x")

    def create_execution_frame(self):
        self.execution_frame = tk.Frame(self.root)
        self.execution_frame.columnconfigure(0, weight=2)
        self.execution_frame.columnconfigure(1, weight=1)
        self.execution_frame.columnconfigure(2, weight=1)

        self.execution_label = tk.Label(self.execution_frame, text="Proceso en Ejecución:", font=("Arial", 15))
        self.execution_label.grid(row=0, column=0, padx=10, pady=0, sticky="w")
        self.execution_data = tk.Label(self.execution_frame, text="", font=("Arial", 10))
        self.execution_data.grid(row=1, column=0, padx=10, pady=0, sticky="w")
        self.execution_time_label = tk.Label(self.execution_frame, text="Tiempo de ejecución:", font=("Arial", 15))
        self.execution_time_label.grid(row=0, column=1, padx=10, pady=0)
        self.execution_time = tk.Label(self.execution_frame, text="", font=("Arial", 12))
        self.execution_time.grid(row=1, column=1, padx=10, pady=0)
        self.remaining_time_label = tk.Label(self.execution_frame, text="Tiempo restante:", font=("Arial", 15))
        self.remaining_time_label.grid(row=0, column=2, padx=10, pady=0)
        self.remaining_time = tk.Label(self.execution_frame, text="", font=("Arial", 12))
        self.remaining_time.grid(row=1, column=2, padx=10, pady=0)

        self.execution_frame.pack(fill="x")

    def create_process_management_frame(self):
        self.multiple_frames = tk.Frame(self.root, bd=2, relief="groove")
        self.multiple_frames.columnconfigure(0, weight=1)
        self.multiple_frames.columnconfigure(1, weight=1)
        self.multiple_frames.columnconfigure(2, weight=1)
        self.multiple_frames.columnconfigure(3, weight=1)

        self.create_capture_process_frame()
        self.create_process_list_frame()
        #self.create_execution_batch_frame()
        self.create_ready_list_frame()
        self.create_finished_process_frame()


        self.multiple_frames.pack(fill="x")

    def create_capture_process_frame(self):
        self.main_frame = tk.Frame(self.multiple_frames)

        self.process_label = tk.Label(self.main_frame, text="Capturar proceso", font=("Arial", 15))

        # New
        def validate_spinbox_input(input):
            if input.isdigit() and 0 <= int(input) <= 100:
                return True
            else:
                return False
        
        validate_command = self.main_frame.register(validate_spinbox_input)

        self.no_process_label = tk.Label(self.main_frame, text="Numero de procesos a ingresar:", font=("Arial", 10))
        self.no_process_input = tk.Spinbox(self.main_frame, from_=0, to=100, font=("Arial", 10), validate='key', validatecommand=(validate_command, '%P'))

        self.submit_button = tk.Button(self.main_frame, text="Capturar", font=("Arial", 10), command=self.capture_process)

        # Packed content
        self.process_label.pack(padx=10, pady=10)
        self.no_process_label.pack(anchor='w', padx=10)
        self.no_process_input.pack(anchor='w', padx=10, pady=0, fill='x')

        self.submit_button.pack(padx=10, pady=10)

        # Add to 'multiple frames'
        self.main_frame.grid(row=0, column=0, padx=0, pady=0)
        
    def create_process_list_frame(self):
        self.list_frame = tk.Frame(self.multiple_frames, width=200, height=275)
        self.list_frame.pack_propagate(False)

        self.list_label = tk.Label(self.list_frame, text="Procesos Nuevos", font=("Arial", 15))
        self.list = tk.Listbox(self.list_frame, font=("Arial", 10))

        # Packed content
        self.list_label.pack(padx=10, pady=10)
        self.list.pack(fill="both", expand=True)

        # Add to 'multiple frames'
        self.list_frame.grid(row=0, column=1, padx=0, pady=0)

    
    def create_ready_list_frame(self):
        self.ready_processes_frame = tk.Frame(self.multiple_frames, width=235, height=275)
        self.ready_processes_frame.pack_propagate(False)

        self.title_ready_frame_label = tk.Label(self.ready_processes_frame, text="Procesos Listos", font=("Arial", 15))
        self.widget_ready_list = tk.Listbox(self.ready_processes_frame, font=("Arial", 10))

        # Packed content
        self.title_ready_frame_label.pack(padx=10, pady=10)
        self.widget_ready_list.pack(fill="both", expand=True)

        # Add to 'multiple frames'
        self.ready_processes_frame.grid(row=0, column=2, padx=0, pady=0)


    def create_finished_process_frame(self):
        self.finished_frame = tk.Frame(self.multiple_frames, width=200, height=275)
        self.finished_frame.pack_propagate(False)

        self.finished_label = tk.Label(self.finished_frame, text="Procesos terminados", font=("Arial", 13))
        self.finished_list = tk.Listbox(self.finished_frame, font=("Arial", 10))

        # Packed content
        self.finished_label.pack(padx=10, pady=10)
        self.finished_list.pack(fill="both", expand=True)

        # Add to 'multiple frames'
        self.finished_frame.grid(row=0, column=3, padx=0, pady=0)


    ########################################################################
    ###################### Functions to handle events ######################
    ########################################################################
    def global_timer(self):
        minutes, seconds = divmod(self.elapsed_time, 60)
        hours, minutes = divmod(minutes, 60)
        self.label.config(text="{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds))
        self.elapsed_time += 1
        self.label.after(1000, self.global_timer)
    

    def capture_process(self):
        def generate_operation():
            def generate_number():
                return random.randint(0, 50)
            def generate_operator():
                operators = ['+', '-', '*', '/', '%']
                return random.choice(operators)
            
            first_number = generate_number()
            operator = generate_operator()
            second_number = generate_number()
            
            return f'{first_number} {operator} {second_number}'
        
        def generate_max_time():
            return random.randint(7, 18)

        no_process = int(self.no_process_input.get())

        i = 0
        while i < no_process:
            id_process = self.id_counter
            self.id_counter += 1

            operation = generate_operation()
            max_time = generate_max_time()

            self.process_list.append({
                "id": id_process,
                "operation": operation,
                "max_time": max_time,
                "exec_time": 0,
                "remaining_time": max_time,
            })

            self.list.insert('end', f"#{id_process} - Tiempo Estimado: {max_time}s")
            i += 1
        
    
    def execution_timer(self):
        if self.execution_time_count < int(self.process['max_time']):
            minutes, seconds = divmod(self.execution_time_count, 60)
            hours, minutes = divmod(minutes, 60)
            self.execution_time.config(text="{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds))

            minutes, seconds = divmod(self.remaining_time_count, 60)
            hours, minutes = divmod(minutes, 60)
            self.remaining_time.config(text="{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds))

            self.execution_time_count += 1
            self.remaining_time_count -= 1

            self.process['exec_time'] += 1
            self.process['remaining_time'] -= 1
            self.current_timer = self.root.after(1000, self.execution_timer)
        else:
            self.widget_ready_list.delete(0)
            self.operate_result()
            self.finished_list.insert(0, f"#{self.process['id']} | {self.process['operation']} = {self.result}")
            self.in_execution.pop(0)            # Clean the process in execution
            
            self.start_simulation_FCFS()


    def operate_result(self):
        self.result = None
        try:
            operation = self.process['operation']
            operation = operation.strip()
            operation = " ".join(operation.split())

            operation_parts = operation.split(" ")
            if len(operation_parts) == 3:
                operator = operation_parts[1]
                if operator == "+":
                    self.result = int(operation_parts[0]) + int(operation_parts[2])
                elif operator == "-":
                    self.result = int(operation_parts[0]) - int(operation_parts[2])
                elif operator == "*":
                    self.result = int(operation_parts[0]) * int(operation_parts[2])
                elif operator == "/":
                    if int(operation_parts[2]) == 0:
                        self.result = "Operacion invalida"
                    else:
                        self.result = round(int(operation_parts[0]) / int(operation_parts[2]), 2)
                elif operator == "%":
                    if int(operation_parts[2]) == 0:
                        self.result = "Operacion invalida"
                    else:
                        self.result = int(operation_parts[0]) % int(operation_parts[2])
                else:
                    self.result = "Operador invalido"
            elif len(operation_parts) == 1:
                self.result = int(operation_parts[0])
            else:
                self.result = "Operacion no soportada"
        except Exception as e:
            self.result = f"Error: {e}"


    def start_simulation_FCFS(self):
        while (len(self.ready_list) + len(self.in_execution) + len(self.blocked_list)) < 3 and self.process_list:
            self.ready_list.append(self.process_list.pop(0))
            self.list.delete(0)
            self.widget_ready_list.insert('end', f"#{self.ready_list[-1]['id']} | Tiempo Estimado: {self.ready_list[-1]['max_time']}s")
        
        if not self.in_execution and self.ready_list:
            self.in_execution.append(self.ready_list.pop(0))
            self.process = self.in_execution[0]
            self.widget_ready_list.delete(0)
            self.execution_data.config(text=f"#{self.process['id']} | Operación: {self.process['operation']} | Tiempo estimado: {self.process['max_time']}s")

            self.execution_time_count = self.process['exec_time']
            self.remaining_time_count = self.process['remaining_time']
            self.execution_timer()
                    
        if not self.process_list and not self.ready_list and not self.in_execution and not self.blocked_list:
            self.execution_data.config(text="")
            self.remaining_batch.config(text="Lotes restantes:\n0")
            self.execution_time.config(text="")
            self.remaining_time.config(text="")
            self.start.config(state="normal")
    

    def stop_process(self, event):
        if self.process:
            self.execution_data.config(text="ERROR")
            self.root.after_cancel(self.current_timer)
            self.root.after(4000, self.resume_stopped_process)
    
    def resume_stopped_process(self):
        self.widget_ready_list.delete(0)
        self.finished_list.insert(0, f"#{self.process['id']} | {self.process['operation']} = ERROR")
        self.start_simulation_batch()

    
    def interrupt_process(self, event):
        if self.process:
            self.execution_data.config(text="INTERRUMPIDO")
            self.blocked_list.append(self.in_execution.pop(0))

            # Adjust the remaining time of the last process to start where it was interrupted
            self.blocked_list[-1]['remaining_time'] += 1
            self.blocked_list[-1]['exec_time'] -= 1
            
            self.root.after_cancel(self.current_timer)
            self.root.after(4000, self.resume_interrupted_process)

    def resume_interrupted_process(self):
        self.start_simulation_FCFS()

        self.root.after(10000, self.reappend_blocked_process)
    
    def reappend_blocked_process(self):
        if self.blocked_list:
            self.ready_list.append(self.blocked_list.pop(0))
            process = self.ready_list[-1]
            self.widget_ready_list.insert('end', f"#{process['id']} | Tiempo Restante: {process['remaining_time']}s")
            self.start_simulation_FCFS()

    def pause_process(self, event):
        if self.process:
            self.execution_data.config(text=f"#{self.process['id']} | Operación: {self.process['operation']} | Tiempo estimado: {self.process['max_time']}s | PAUSADO")
            self.is_paused = True
            self.root.after_cancel(self.current_timer)

    def continue_process(self, event):
        if self.process and self.is_paused:
            self.execution_data.config(text=f"#{self.process['id']} | Operación: {self.process['operation']} | Tiempo estimado: {self.process['max_time']}s")
            self.current_timer = self.root.after(1000, self.execution_timer)
            self.is_paused = False
    

    def start_simulation(self):
        self.start.config(state="disabled")
        self.start_simulation_FCFS()


if __name__ == "__main__":
    root = tk.Tk()
    app = BatchProcess(root)
    root.mainloop()