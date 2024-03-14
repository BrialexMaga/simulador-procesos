import tkinter as tk
from tkinter import ttk
import random
import time

class BatchProcess:
    def __init__(self, root):
        # variables
        self.id_counter = 0     # Global counter for process id
        self.elapsed_time = 0   # Global timer
        self.process_list = []  # New processes, not ready
        self.ready_list = []
        self.in_execution = []
        self.blocked_list = []
        self.finished_processes_list = []

        self.current_timer = None
        self.process = None
        self.is_paused = False
        self.update_scheduled = False   # To avoid multiple updates of the blocked time
        self.started_simulation = False

        # Window configuration
        self.root = root
        self.root.title("Practica 2")
        self.root.geometry("1120x675")
        self.root.resizable(False, False)
        self.create_widgets()

        # New key binds
        self.root.bind('e', self.interrupt_process)     # Interrupt process
        self.root.bind('w', self.stop_process)          # Error Binding
        self.root.bind('p', self.pause_process)         # Pause process
        self.root.bind('c', self.continue_process)      # Continue process
        self.root.bind('n', self.create_new_process)    # Create new process
        self.root.bind('b', self.show_processes_table)  # Show processes table
    
    def create_widgets(self):
        self.create_header_frame()
        self.create_execution_frame()
        self.create_process_management_frame()
        self.create_times_list_frame()
    
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
        self.remaining_batch = tk.Label(self.header_frame, text="", font=("Arial", 15))
        self.remaining_batch.grid(row=0, column=2, padx=15, pady=10, sticky="E")

        # Global Timer inside header
        self.label = tk.Label(self.header_frame, text="00:00:00", font=("Arial", 20))
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
        self.multiple_frames.columnconfigure(4, weight=1)

        self.create_capture_process_frame()
        self.create_process_list_frame()
        
        self.create_ready_list_frame()
        self.create_blocked_process_frame()
        self.create_finished_process_frame()

        self.multiple_frames.pack(fill="x")

    def create_capture_process_frame(self):
        self.main_frame = tk.Frame(self.multiple_frames)

        self.process_label = tk.Label(self.main_frame, text="Capturar proceso", font=("Arial", 15))

        # New
        def validate_spinbox_input(input):
            if input.isdigit() and 1 <= int(input) <= 100:
                return True
            else:
                return False
        
        validate_command = self.main_frame.register(validate_spinbox_input)

        self.spin_value = tk.IntVar(value=1)

        self.no_process_label = tk.Label(self.main_frame, text="Numero de procesos a ingresar:", font=("Arial", 10))
        self.no_process_input = tk.Spinbox(self.main_frame, from_=0, to=100, textvariable=self.spin_value, font=("Arial", 10), validate='key', validatecommand=(validate_command, '%P'))

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


    def create_blocked_process_frame(self):
        self.blocked_frame = tk.Frame(self.multiple_frames, width=235, height=275)
        self.blocked_frame.pack_propagate(False)

        self.blocked_label = tk.Label(self.blocked_frame, text="Procesos Bloqueados", font=("Arial", 15))
        self.widget_blocked_list = tk.Listbox(self.blocked_frame, font=("Arial", 10))

        # Packed content
        self.blocked_label.pack(padx=10, pady=10)
        self.widget_blocked_list.pack(fill="both", expand=True)

        # Add to 'multiple frames'
        self.blocked_frame.grid(row=0, column=3, padx=0, pady=0)
    

    def create_finished_process_frame(self):
        self.finished_frame = tk.Frame(self.multiple_frames, width=235, height=275)
        self.finished_frame.pack_propagate(False)

        self.finished_label = tk.Label(self.finished_frame, text="Procesos terminados", font=("Arial", 15))
        self.finished_list = tk.Listbox(self.finished_frame, font=("Arial", 10))

        # Packed content
        self.finished_label.pack(padx=10, pady=10)
        self.finished_list.pack(fill="both", expand=True)

        # Add to 'multiple frames'
        self.finished_frame.grid(row=0, column=4, padx=0, pady=0)
    

    def create_times_list_frame(self):
        self.times_frame = tk.Frame(self.root, padx=150, pady=10)

        self.times_label = tk.Label(self.times_frame, text="Lista de tiempos", font=("Arial", 15))
        self.widget_times_list = tk.Listbox(self.times_frame, height=12, font=("Arial", 10))

        # Packed content
        self.times_label.pack(padx=10, pady=10)
        self.widget_times_list.pack(fill="both", expand=True)

        # Add to 'multiple frames'
        self.times_frame.pack(fill="x")


    ########################################################################
    ###################### Functions to handle events ######################
    ########################################################################
    def global_timer(self):
        if not self.process_list and not self.ready_list and not self.in_execution and not self.blocked_list:
            return  # Stop the timer when all processes are done
    
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
        self.spin_value.set(1)

        i = 0
        while i < no_process:
            id_process = self.id_counter
            self.id_counter += 1

            operation = generate_operation()
            max_time = generate_max_time()

            self.process_list.append({
                "id": id_process,
                "operation": operation,
                "result": "Dummy",
                "max_time": max_time,
                "exec_time": 0,
                "remaining_time": max_time,
                "blocked_time": 0,
                "start_time": 0,
                "end_time": 0,
                "return_time": 0,
                "response_time": 0,
                "waiting_time": 0,
                "service_time": 0,
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
            self.finished_processes_list.append(self.in_execution.pop(0))   # Clean the process in execution, save in finished list
            
            self.finished_processes_list[-1]['result'] = self.result
            self.finished_processes_list[-1]['end_time'] = self.elapsed_time - 1
            self.finished_processes_list[-1]['response_time'] = self.process['response_time']
            self.finished_processes_list[-1]['service_time'] = self.finished_processes_list[-1]['max_time']

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
        # Load new processes to ready list
        while (len(self.ready_list) + len(self.in_execution) + len(self.blocked_list)) < 3 and self.process_list:
            self.ready_list.append(self.process_list.pop(0))
            self.ready_list[-1]['start_time'] = self.elapsed_time - 1
            self.list.delete(0)
            self.widget_ready_list.insert('end', f"#{self.ready_list[-1]['id']} | Estimado: {self.ready_list[-1]['max_time']}s | Restante: {self.ready_list[-1]['remaining_time']}s")
        
        # Load a ready process to execution
        if not self.in_execution and self.ready_list:
            self.in_execution.append(self.ready_list.pop(0))
            self.process = self.in_execution[0]
            self.process['response_time'] = abs(self.elapsed_time - self.process['start_time'])
            self.process['waiting_time'] += abs(self.elapsed_time - self.process['start_time'])
            self.execution_data.config(text=f"#{self.process['id']} | Operación: {self.process['operation']} | Tiempo estimado: {self.process['max_time']}s")

            self.execution_time_count = self.process['exec_time']
            self.remaining_time_count = self.process['remaining_time']
            self.execution_timer()
        
        # If everything is done, stop the simulation and clean
        if not self.process_list and not self.ready_list and not self.in_execution and not self.blocked_list:
            self.execution_data.config(text="")
            #self.remaining_batch.config(text="Lotes restantes:\n0")    # Reset the batch counter, but deprecated
            self.execution_time.config(text="")
            self.remaining_time.config(text="")

            self.show_times()
            self.start.config(state="normal")
            self.started_simulation = False
    

    def show_times(self):
        self.widget_times_list.delete(0, 'end')
        for process in self.finished_processes_list:
            process['return_time'] = abs(process['end_time'] - process['start_time'])
            self.widget_times_list.insert('end', f"#{process['id']} | {process['operation']} = {process['result']} | Tiempo estimado: {process['max_time']} | Inicio: {process['start_time']}s | Finalización: {process['end_time']}s | Retorno: {process['return_time']}s | Respuesta: {process['response_time']}s | Espera: {process['waiting_time']}s | Servicio: {process['service_time']}s")
        

    def stop_process(self, event):
        if self.process:
            self.execution_data.config(text="ERROR")
            self.root.after_cancel(self.current_timer)
            self.root.after(1, self.resume_stopped_process)
    
    def resume_stopped_process(self):
        self.widget_ready_list.delete(0)
        self.process['result'] = "ERROR"
        self.finished_list.insert(0, f"#{self.process['id']} | {self.process['operation']} = {self.process['result']}")

        # Clean the process in execution
        self.finished_processes_list.append(self.in_execution.pop(0))
        self.finished_processes_list[-1]['end_time'] = self.elapsed_time - 1
        self.finished_processes_list[-1]['service_time'] = self.process['exec_time'] - 1
        self.in_execution = []
        self.process = None
        self.start_simulation_FCFS()

    
    def interrupt_process(self, event):
        if self.process:
            self.execution_data.config(text="INTERRUMPIDO")
            self.blocked_list.append(self.in_execution.pop(0))
            self.widget_ready_list.delete(0)

            # Adjust the remaining time of the last process to start where it was interrupted
            self.blocked_list[-1]['remaining_time'] += 1
            self.blocked_list[-1]['exec_time'] -= 1
            self.blocked_list[-1]['blocked_time'] = 0
            
            self.root.after_cancel(self.current_timer)
            self.root.after(1, self.resume_interrupted_process)

    def resume_interrupted_process(self):
        if not self.update_scheduled:
            self.root.after(1000, self.update_blocked_time)
            self.update_scheduled = True
        
        blocked_time = 9000
        self.root.after(blocked_time, self.reappend_blocked_process)
        self.start_simulation_FCFS()
    
    def update_blocked_time(self):
        for i, process in enumerate(self.blocked_list):
            process['blocked_time'] += 1
            self.widget_blocked_list.delete(i)
            self.widget_blocked_list.insert(i, f"#{process['id']} | Bloqueado: {process['blocked_time']}s")

        if self.blocked_list:  # If there are still blocked processes, schedule the next update
            self.root.after(1000, self.update_blocked_time)
        else:
            self.update_scheduled = False
    
    def reappend_blocked_process(self):
        if self.blocked_list:
            process = self.blocked_list.pop(0)
            self.widget_blocked_list.delete(0)
            self.ready_list.append(process)
            self.ready_list[-1]['waiting_time'] += abs(self.elapsed_time - self.ready_list[-1]['blocked_time'])
            self.widget_ready_list.insert('end', f"#{process['id']} | Estimado: {process['max_time']}s | Restante: {process['remaining_time']}s")
            
            self.start_simulation_FCFS()
        
        if not self.blocked_list:
            self.update_scheduled = False

    def pause_process(self, event):
        if self.process:
            self.execution_data.config(text=f"#{self.process['id']} | Operación: {self.process['operation']} | Tiempo estimado: {self.process['max_time']}s | PAUSADO")
            self.is_paused = True
            self.root.after_cancel(self.current_timer)
            self.root.after_cancel(self.global_timer)

    def continue_process(self, event):
        if self.process and self.is_paused:
            self.execution_data.config(text=f"#{self.process['id']} | Operación: {self.process['operation']} | Tiempo estimado: {self.process['max_time']}s")
            self.current_timer = self.root.after(1000, self.execution_timer)
            self.is_paused = False
    

    def create_new_process(self, event):
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

        # Add a new process to the list
        id_process = self.id_counter
        self.id_counter += 1

        operation = generate_operation()
        max_time = generate_max_time()

        self.process_list.append({
                "id": id_process,
                "operation": operation,
                "result": "Dummy",
                "max_time": max_time,
                "exec_time": 0,
                "remaining_time": max_time,
                "blocked_time": 0,
                "start_time": 0,
                "end_time": 0,
                "return_time": 0,
                "response_time": 0,
                "waiting_time": 0,
                "service_time": 0,
            })

        self.list.insert('end', f"#{id_process} - Tiempo Estimado: {max_time}s")

        # If the simulation has started, load the new process to the ready list to a max of 3
        while (len(self.ready_list) + len(self.in_execution) + len(self.blocked_list)) < 3 and self.process_list and self.started_simulation:
            self.ready_list.append(self.process_list.pop(0))
            self.ready_list[-1]['start_time'] = self.elapsed_time - 1
            self.list.delete(0)
            self.widget_ready_list.insert('end', f"#{self.ready_list[-1]['id']} | Estimado: {self.ready_list[-1]['max_time']}s | Restante: {self.ready_list[-1]['remaining_time']}s")
        

    def show_processes_table(self, event):
        self.pause_process(event)

        # Create a new window
        process_window = tk.Toplevel(self.root)
        process_window.title("Tabla de Procesos")

        # Show the process table
        tree = ttk.Treeview(process_window, columns=("ID", "Estado", "Operacion", "llegada", "Finalizacion", "Retorno", "Espera", "Servicio", "Restante en CPU", "Respuesta"), show="headings")
        tree.heading('ID', text="ID")
        tree.heading('Estado', text="Estado")
        tree.heading('Operacion', text="Operación")
        tree.heading('llegada', text="Llegada")
        tree.heading('Finalizacion', text="Finalización")
        tree.heading('Retorno', text="Retorno")
        tree.heading('Espera', text="Espera")
        tree.heading('Servicio', text="Servicio")
        tree.heading('Restante en CPU', text="Restante en CPU")
        tree.heading('Respuesta', text="Respuesta")

        tree.column('ID', width=50, anchor='center')
        tree.column('Estado', width=100, anchor='center')
        tree.column('Operacion', anchor='center')
        tree.column('llegada', width=100, anchor='center')
        tree.column('Finalizacion', width=100, anchor='center')
        tree.column('Retorno', width=100, anchor='center')
        tree.column('Espera', width=100, anchor='center')
        tree.column('Servicio', width=100, anchor='center')
        tree.column('Restante en CPU', width=100, anchor='center')
        tree.column('Respuesta', width=100, anchor='center')

        tree.pack(pady=10, padx=10, fill="x", expand=True)

        # Show the process table
        for process in self.process_list:
            tree.insert("", "end", values=(process['id'], "Nuevo", process['operation'], process['start_time'], "", "", "", "", process['remaining_time'], ""))
        
        for process in self.ready_list:
            tree.insert("", "end", values=(process['id'], "Listo", process['operation'], process['start_time'], "", "", process['waiting_time'], "", process['remaining_time'], ""))

        for process in self.in_execution:
            tree.insert("", "end", values=(process['id'], "Ejecución", process['operation'], process['start_time'], "", process['return_time'], process['waiting_time'], process['service_time'], process['remaining_time'], process['response_time']))

        for process in self.blocked_list:
            tree.insert("", "end", values=(process['id'], "Bloqueado", process['operation'], process['start_time'], "", process['return_time'], process['waiting_time'], process['service_time'], process['remaining_time'], process['response_time']))
        
        for process in self.finished_processes_list:
            tree.insert("", "end", values=(process['id'], "Terminado", f"{process['operation']} = {process['result']}", process['start_time'], process['end_time'], process['return_time'], process['waiting_time'], process['service_time'], "", process['response_time']))
    

    def start_simulation(self):
        self.start.config(state="disabled")
        self.started_simulation = True
        self.elapsed_time = 0
        self.global_timer()
        self.start_simulation_FCFS()


if __name__ == "__main__":
    root = tk.Tk()
    app = BatchProcess(root)
    root.mainloop()