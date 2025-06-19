from customtkinter import *
import pymysql
import pandas as pd








# conexão com banco
conexao = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='escola',
    port=3306,
)
cursor = conexao.cursor()

import customtkinter as ctk
import pymysql
import pandas as pd
from tkinter import messagebox, Toplevel, Label, Text, Button



# --- CONFIGURAÇÕES DO BANCO DE DADOS MySQL ---
DB_CONFIG = {
'host' : 'localhost',
'user' : 'root',
'password' : '',
'database' : 'escola',
'port' : 3306,
}
# --- FIM DAS CONFIGURAÇÕES ---

# Configurações iniciais do CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


# Função para obter a conexão com o banco de dados MySQL
def get_db_connection():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except pymysql.Error as err:
        messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao banco de dados: {err}\n"
                                                "Verifique as configurações em DB_CONFIG e se o servidor MySQL está rodando.")
        return None


# Função para criar as tabelas no MySQL se não existirem
def create_tables():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cursos (
                    id_curso INT AUTO_INCREMENT PRIMARY KEY,
                    nome_curso VARCHAR(255) NOT NULL UNIQUE,
                    descricao TEXT,
                    duracao VARCHAR(100)
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alunos (
                    id_aluno INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL,
                    cpf VARCHAR(14) NOT NULL UNIQUE,
                    email VARCHAR(255),
                    id_curso INT,
                    FOREIGN KEY (id_curso) REFERENCES cursos(id_curso) ON DELETE SET NULL
                );
            """)
            conn.commit()
            print("Tabelas verificadas/criadas no MySQL com sucesso!")
        except pymysql.connector.Error as err:
            messagebox.showerror("Erro SQL", f"Erro ao criar tabelas: {err}")
        finally:
            cursor.close()
            conn.close()


# --- Funções CRUD para Cursos ---
def cadastrar_curso(nome, descricao, duracao, nova_janela_curso_ref):
    if not nome:
        messagebox.showerror("Erro", "Nome do curso é obrigatório.")
        return

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO cursos (nome_curso, descricao, duracao) VALUES (%s, %s, %s)",
                           (nome, descricao, duracao))
            conn.commit()
            messagebox.showinfo("Sucesso", "Curso cadastrado!")
            nova_janela_curso_ref.destroy()  # Fecha a janela após cadastro
        except pymysql.connector.Error as err:
            if err.errno == pymysql.connector.errorcode.ER_DUP_ENTRY:
                messagebox.showerror("Erro", "Curso com este nome já existe.")
            else:
                messagebox.showerror("Erro", f"Erro ao cadastrar curso: {err}")
        finally:
            cursor.close()
            conn.close()


def ler_cursos():
    conn = get_db_connection()
    if conn:
        try:
            df = pd.read_sql_query("SELECT * FROM cursos", conn)
            if not df.empty:
                # Cria uma nova janela para exibir os dados
                display_window = ctk.CTkToplevel(janela)
                display_window.title("Cursos Cadastrados")
                display_window.geometry("600x400")

                text_display = ctk.CTkTextbox(display_window, wrap="none", activate_scrollbars=True)
                text_display.pack(expand=True, fill="both", padx=10, pady=10)
                text_display.insert("1.0", df.to_string(index=False))
                text_display.configure(state="disabled")
            else:
                messagebox.showinfo("Cursos", "Nenhum curso cadastrado.")
        except pymysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao ler cursos: {err}")
        finally:
            conn.close()


def excluir_curso(id_curso):
    if not id_curso:
        messagebox.showerror("Erro", "ID do curso é obrigatório para exclusão.")
        return

    if not messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o curso com ID {id_curso}?"):
        return

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM cursos WHERE id_curso=%s", (id_curso,))
            if cursor.rowcount > 0:
                conn.commit()
                messagebox.showinfo("Sucesso", "Curso excluído.")
            else:
                messagebox.showerror("Erro", "ID do curso não encontrado.")
        except pymysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao excluir curso: {err}")
        finally:
            cursor.close()
            conn.close()


def atualizar_curso(id_curso, nome, descricao, duracao, nova_janela_curso_ref):
    if not id_curso or not nome:
        messagebox.showerror("Erro", "ID e Nome do curso são obrigatórios para atualização.")
        return

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE cursos SET nome_curso=%s, descricao=%s, duracao=%s WHERE id_curso=%s",
                           (nome, descricao, duracao, id_curso))
            if cursor.rowcount > 0:
                conn.commit()
                messagebox.showinfo("Sucesso", "Curso atualizado.")
                nova_janela_curso_ref.destroy()
            else:
                messagebox.showerror("Erro", "ID do curso não encontrado.")
        except pymysql.connector.Error as err:
            if err.errno == pymysql.connector.errorcode.ER_DUP_ENTRY:
                messagebox.showerror("Erro", "Outro curso com este nome já existe.")
            else:
                messagebox.showerror("Erro", f"Erro ao atualizar curso: {err}")
        finally:
            cursor.close()
            conn.close()


# --- Funções CRUD para Alunos ---
def cadastrar_aluno(nome, cpf, email, id_curso_selecionado):
    if not nome or not cpf:
        messagebox.showerror("Erro", "Nome e CPF do aluno são obrigatórios.")
        return

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO alunos (nome, cpf, email, id_curso) VALUES (%s, %s, %s, %s)",
                           (nome, cpf, email, id_curso_selecionado))
            conn.commit()
            messagebox.showinfo("Sucesso", "Aluno cadastrado!")
            # Limpa os campos da janela principal
            entry_nome_aluno.delete(0, ctk.END)
            entry_cpf_aluno.delete(0, ctk.END)
            entry_email_aluno.delete(0, ctk.END)
            # Reseta o menu de curso
            update_course_options(option_menu_cursos_aluno)

        except pymysql.connector.Error as err:
            if err.errno == pymysql.connector.errorcode.ER_DUP_ENTRY:
                messagebox.showerror("Erro", "Aluno com este CPF já existe.")
            else:
                messagebox.showerror("Erro", f"Erro ao cadastrar aluno: {err}")
        finally:
            cursor.close()
            conn.close()


def ler_alunos():
    conn = get_db_connection()
    if conn:
        try:
            df = pd.read_sql_query("""
                SELECT 
                    a.id_aluno, 
                    a.nome, 
                    a.cpf, 
                    a.email, 
                    c.nome_curso AS curso 
                FROM 
                    alunos a
                LEFT JOIN 
                    cursos c ON a.id_curso = c.id_curso
            """, conn)
            if not df.empty:
                # Cria uma nova janela para exibir os dados
                display_window = ctk.CTkToplevel(janela)
                display_window.title("Alunos Cadastrados")
                display_window.geometry("700x500")

                text_display = ctk.CTkTextbox(display_window, wrap="none", activate_scrollbars=True)
                text_display.pack(expand=True, fill="both", padx=10, pady=10)
                text_display.insert("1.0", df.to_string(index=False))
                text_display.configure(state="disabled")
            else:
                messagebox.showinfo("Alunos", "Nenhum aluno cadastrado.")
        except pymysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao ler alunos: {err}")
        finally:
            conn.close()


def excluir_aluno(id_aluno):
    if not id_aluno:
        messagebox.showerror("Erro", "ID do aluno é obrigatório para exclusão.")
        return

    if not messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o aluno com ID {id_aluno}?"):
        return

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM alunos WHERE id_aluno=%s", (id_aluno,))
            if cursor.rowcount > 0:
                conn.commit()
                messagebox.showinfo("Sucesso", "Aluno excluído.")
            else:
                messagebox.showerror("Erro", "ID do aluno não encontrado.")
        except pymysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao excluir aluno: {err}")
        finally:
            cursor.close()
            conn.close()


def atualizar_aluno(id_aluno, nome, cpf, email, id_curso_selecionado):
    if not id_aluno or not nome or not cpf:
        messagebox.showerror("Erro", "ID, Nome e CPF do aluno são obrigatórios para atualização.")
        return

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE alunos SET nome=%s, cpf=%s, email=%s, id_curso=%s WHERE id_aluno=%s",
                           (nome, cpf, email, id_curso_selecionado, id_aluno))
            if cursor.rowcount > 0:
                conn.commit()
                messagebox.showinfo("Sucesso", "Aluno atualizado.")
                # Limpa os campos da janela principal
                entry_id_aluno.delete(0, ctk.END)  # Novo campo para ID do aluno
                entry_nome_aluno.delete(0, ctk.END)
                entry_cpf_aluno.delete(0, ctk.END)
                entry_email_aluno.delete(0, ctk.END)
                update_course_options(option_menu_cursos_aluno)
            else:
                messagebox.showerror("Erro", "ID do aluno não encontrado.")
        except pymysql.connector.Error as err:
            if err.errno == pymysql.connector.errorcode.ER_DUP_ENTRY:
                messagebox.showerror("Erro", "Outro aluno com este CPF já existe.")
            else:
                messagebox.showerror("Erro", f"Erro ao atualizar aluno: {err}")
        finally:
            cursor.close()
            conn.close()


# --- Funções Auxiliares da Interface ---

# Mapa para converter nome de curso em ID e vice-versa
course_id_map = {}


def update_course_options(option_menu):
    """Atualiza as opções do CTkOptionMenu com os cursos disponíveis."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id_curso, nome_curso FROM cursos ORDER BY nome_curso")
            courses = cursor.fetchall()

            options = ["Nenhum Curso (ID: None)"]
            course_id_map.clear()
            course_id_map["Nenhum Curso (ID: None)"] = None

            for id_curso, nome_curso in courses:
                display_name = f"{nome_curso} (ID: {id_curso})"
                options.append(display_name)
                course_id_map[display_name] = id_curso

            option_menu.configure(values=options)
            option_menu.set(options[0])  # Seleciona a primeira opção por padrão
        except pymysql.connector.Error as err:
            messagebox.showerror("Erro SQL", f"Erro ao carregar opções de curso: {err}")
        finally:
            cursor.close()
            conn.close()


# Função para abrir a janela de curso
def abrir_janela_curso():
    nova_janela_curso = ctk.CTkToplevel(janela)
    nova_janela_curso.title("Cadastro/Atualização de Curso")
    nova_janela_curso.geometry("450x450")  # Aumentado um pouco para botões de CRUD

    # Campos de entrada
    ctk.CTkLabel(nova_janela_curso, text="ID do Curso (para Atualizar/Excluir):").grid(column=0, row=0, padx=10, pady=5,
                                                                                       sticky="e")
    entry_id_curso = ctk.CTkEntry(nova_janela_curso, width=200)
    entry_id_curso.grid(column=1, row=0, padx=10, pady=5)

    ctk.CTkLabel(nova_janela_curso, text="Nome do Curso:").grid(column=0, row=1, padx=10, pady=5, sticky="e")
    entry_nome_curso = ctk.CTkEntry(nova_janela_curso, width=200)
    entry_nome_curso.grid(column=1, row=1, padx=10, pady=5)

    ctk.CTkLabel(nova_janela_curso, text="Descrição:").grid(column=0, row=2, padx=10, pady=5, sticky="e")
    entry_descricao_curso = ctk.CTkEntry(nova_janela_curso, width=200)
    entry_descricao_curso.grid(column=1, row=2, padx=10, pady=5)

    ctk.CTkLabel(nova_janela_curso, text="Duração (horas):").grid(column=0, row=3, padx=10, pady=5, sticky="e")
    entry_duracao_curso = ctk.CTkEntry(nova_janela_curso, width=200)
    entry_duracao_curso.grid(column=1, row=3, padx=10, pady=5)

    # Botões de Ação para Curso (CRUD)
    ctk.CTkButton(nova_janela_curso, text="Cadastrar", command=lambda: cadastrar_curso(
        entry_nome_curso.get(), entry_descricao_curso.get(), entry_duracao_curso.get(), nova_janela_curso
    )).grid(column=0, row=4, columnspan=2, pady=5)

    ctk.CTkButton(nova_janela_curso, text="Ler Cursos", command=ler_cursos).grid(column=0, row=5, columnspan=2, pady=5)

    ctk.CTkButton(nova_janela_curso, text="Atualizar", command=lambda: atualizar_curso(
        entry_id_curso.get(), entry_nome_curso.get(), entry_descricao_curso.get(), entry_duracao_curso.get(),
        nova_janela_curso
    )).grid(column=0, row=6, columnspan=2, pady=5)

    ctk.CTkButton(nova_janela_curso, text="Excluir", command=lambda: excluir_curso(
        entry_id_curso.get()
    )).grid(column=0, row=7, columnspan=2, pady=5)


# --- Janela Principal (Cadastro de Alunos) ---
janela = ctk.CTk()
janela.title("Cadastro de Alunos")
janela.geometry("400x550")  # Aumentado para acomodar mais botões

# Campos de entrada de aluno
ctk.CTkLabel(janela, text="ID do Aluno (para Atualizar/Excluir):").grid(column=0, row=0, padx=10, pady=5, sticky="e")
entry_id_aluno = ctk.CTkEntry(janela, width=200)
entry_id_aluno.grid(column=1, row=0, padx=10, pady=5)

ctk.CTkLabel(janela, text="Nome do Aluno:").grid(column=0, row=1, padx=10, pady=5, sticky="e")
entry_nome_aluno = ctk.CTkEntry(janela, width=200)
entry_nome_aluno.grid(column=1, row=1, padx=10, pady=5)

ctk.CTkLabel(janela, text="CPF:").grid(column=0, row=2, padx=10, pady=5, sticky="e")
entry_cpf_aluno = ctk.CTkEntry(janela, width=200)
entry_cpf_aluno.grid(column=1, row=2, padx=10, pady=5)

ctk.CTkLabel(janela, text="Email:").grid(column=0, row=3, padx=10, pady=5, sticky="e")
entry_email_aluno = ctk.CTkEntry(janela, width=200)
entry_email_aluno.grid(column=1, row=3, padx=10, pady=5)

ctk.CTkLabel(janela, text="Curso:").grid(column=0, row=4, padx=10, pady=5, sticky="e")
option_menu_cursos_aluno = ctk.CTkOptionMenu(janela, values=["Carregando..."])
option_menu_cursos_aluno.grid(column=1, row=4, padx=10, pady=5, sticky="ew")

# Botões de Ação para Aluno (CRUD)
ctk.CTkButton(janela, text="Cadastrar Aluno", command=lambda: cadastrar_aluno(
    entry_nome_aluno.get(), entry_cpf_aluno.get(), entry_email_aluno.get(),
    course_id_map.get(option_menu_cursos_aluno.get())  # Pega o ID do curso selecionado
)).grid(column=0, row=5, columnspan=2, pady=5)

ctk.CTkButton(janela, text="Ler Alunos", command=ler_alunos).grid(column=0, row=6, columnspan=2, pady=5)

ctk.CTkButton(janela, text="Atualizar Aluno", command=lambda: atualizar_aluno(
    entry_id_aluno.get(), entry_nome_aluno.get(), entry_cpf_aluno.get(), entry_email_aluno.get(),
    course_id_map.get(option_menu_cursos_aluno.get())
)).grid(column=0, row=7, columnspan=2, pady=5)

ctk.CTkButton(janela, text="Excluir Aluno", command=lambda: excluir_aluno(
    entry_id_aluno.get()
)).grid(column=0, row=8, columnspan=2, pady=5)

ctk.CTkButton(janela, text="Abrir Cadastro de Curso", command=abrir_janela_curso).grid(column=0, row=9, columnspan=2,
                                                                                       pady=10)

# --- Inicialização ---
create_tables()  # Garante que as tabelas existam ao iniciar
update_course_options(option_menu_cursos_aluno)  # Carrega os cursos para o OptionMenu do aluno

janela.mainloop()
