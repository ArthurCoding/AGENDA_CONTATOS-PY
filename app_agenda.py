import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# --- configuração global ---
DB_NOME = 'agenda_contatos.db'
# variável global para rastrear o ID do contato que está sendo editado.
ID_EM_EDICAO = None

# --- funções do Banco de Dados (CRUD) ---

def conectar_db():
    """cria a conexão e garante que a tabela contatos exista."""
    conn = sqlite3.connect(DB_NOME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Contatos (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL,
            email TEXT
        )
    ''')
    conn.commit()
    return conn, cursor

def adicionar_contato(nome, telefone, email):
    """cnsere um novo contato no banco de dados (CREATE)."""
    conn, cursor = conectar_db()
    try:
        cursor.execute(
            "INSERT INTO Contatos (nome, telefone, email) VALUES (?, ?, ?)",
            (nome, telefone, email)
        )
        conn.commit()
        messagebox.showinfo("sucesso", "contato adicionado com sucesso!")
        carregar_contatos() # atualiza a lista
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao adicionar contato: {e}")
    finally:
        conn.close()

def atualizar_contato(contato_id, nome, telefone, email):
    """atualiza um contato existente no banco de dados (UPDATE)."""
    conn, cursor = conectar_db()
    try:
        cursor.execute(
            "UPDATE Contatos SET nome = ?, telefone = ?, email = ? WHERE id = ?",
            (nome, telefone, email, contato_id)
        )
        conn.commit()
        messagebox.showinfo("Sucesso", "Contato atualizado com sucesso!")
        carregar_contatos() # stualiza a lista
        cancelar_edicao() # limpa os campos e redefine
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao atualizar contato: {e}")
    finally:
        conn.close()

def carregar_contatos():
    """Busca todos os contatos e atualiza a Treeview (READ)."""
    # limpa a treeview
    for i in tree.get_children():
        tree.delete(i)
    
    conn, cursor = conectar_db()
    try:
        #  estamos selecionando o ID, mas ele fica oculto, apenas usado internamente
        cursor.execute("SELECT id, nome, telefone, email FROM Contatos ORDER BY nome")
        contatos = cursor.fetchall()
        # insere os dados na Treeview
        for contato in contatos:
            # contato[0] é o ID (não exibido), contato[1:] são os valores exibidos
            tree.insert('', tk.END, text=contato[0], values=contato[1:]) 
            
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar contatos: {e}")
    finally:
        conn.close()

def excluir_contato():
    """exclui o contato selecionado na Treeview (DELETE)."""
    selected_item = tree.focus() # pega o item selecionado
    if not selected_item:
        messagebox.showwarning("Atenção", "Selecione um contato para excluir.")
        return

    # O 'text' de um item da Treeview armazena o ID (que é o que realmente precisamos para a excluir)
    contato_id = tree.item(selected_item, 'text')
    nome_selecionado = tree.item(selected_item, 'values')[0]

    confirmar = messagebox.askyesno(
        "Confirmação",
        f"Tem certeza que deseja excluir o contato: {nome_selecionado}?"
    )

    if confirmar:
        conn, cursor = conectar_db()
        try:
            cursor.execute("DELETE FROM Contatos WHERE id = ?", (contato_id,))
            conn.commit()
            messagebox.showinfo("Sucesso", "Contato excluído com sucesso!")
            carregar_contatos() # atualiza a lista
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir contato: {e}")
        finally:
            conn.close()

# --- funções de ação da interface gráfica (Edit/Save Handler) ---

def salvar_contato_handler():
    """Gerencia a ação do botão principal: INSERT ou UPDATE."""
    global ID_EM_EDICAO

    nome = entry_nome.get().strip()
    telefone = entry_telefone.get().strip()
    email = entry_email.get().strip()

    if not nome or not telefone:
        messagebox.showwarning("Atenção", "Os campos Nome e Telefone são obrigatórios.")
        return

    if ID_EM_EDICAO is None:
        # se ID_EM_EDICAO for None, estamos adicionando um novo contato
        adicionar_contato(nome, telefone, email)
        # limpa os campos após a inserção
        entry_nome.delete(0, tk.END)
        entry_telefone.delete(0, tk.END)
        entry_email.delete(0, tk.END)
    else:
        # se ID_EM_EDICAO tiver um valor, estamos editando
        atualizar_contato(ID_EM_EDICAO, nome, telefone, email)


def carregar_para_edicao():
    """Carrega os dados do contato selecionado para os campos de entrada."""
    global ID_EM_EDICAO
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showwarning("Atenção", "Selecione um contato para editar.")
        return

    #  obter o ID e os dados do item selecionado
    ID_EM_EDICAO = tree.item(selected_item, 'text')
    nome, telefone, email = tree.item(selected_item, 'values')

    # limpar e preencher os campos de entrada
    entry_nome.delete(0, tk.END)
    entry_telefone.delete(0, tk.END)
    entry_email.delete(0, tk.END)

    entry_nome.insert(0, nome)
    entry_telefone.insert(0, telefone)
    entry_email.insert(0, email)

    # 3. atualizar a interface gráfica para o modo edição
    btn_salvar.config(text="💾 Salvar Edição")
    btn_cancelar.grid(row=3, column=2, padx=5, pady=10) # mostra o botão cancelar
    
    messagebox.showinfo("Modo Edição", f"Você está editando o contato: {nome}. Clique em 'Salvar Edição' ou 'Cancelar'.")

def cancelar_edicao():
    """Limpa o estado de edição e redefine a GUI."""
    global ID_EM_EDICAO
    ID_EM_EDICAO = None
    
    #  limpar os campos
    entry_nome.delete(0, tk.END)
    entry_telefone.delete(0, tk.END)
    entry_email.delete(0, tk.END)
    
    #  Resetar o botão principal
    btn_salvar.config(text="➕ Adicionar Contato")
    
    #  Ocultar o botão Cancelar
    btn_cancelar.grid_remove() 


# --- configuração da Interface Gráfica (GUI) ---

#  cria a Janela Principal
janela = tk.Tk()
janela.title("📝 Agenda de Contatos - Python/SQLite3")
janela.geometry("700x500") # Aumentei um pouco a janela

#  frame de Entrada de Dados
frame_entrada = ttk.LabelFrame(janela, text="Adicionar / Editar Contato")
frame_entrada.pack(padx=10, pady=10, fill="x")

# campos de Entrada
ttk.Label(frame_entrada, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_nome = ttk.Entry(frame_entrada, width=30)
entry_nome.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

ttk.Label(frame_entrada, text="Telefone:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
entry_telefone = ttk.Entry(frame_entrada, width=30)
entry_telefone.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

ttk.Label(frame_entrada, text="Email:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
entry_email = ttk.Entry(frame_entrada, width=30)
entry_email.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

# botões de Ação (Salvar e Cancelar Edição)
btn_salvar = ttk.Button(frame_entrada, text="➕ Adicionar Contato", command=salvar_contato_handler)
btn_salvar.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

btn_cancelar = ttk.Button(frame_entrada, text="Cancelar Edição", command=cancelar_edicao)
# de inicio, o botão Cancelar fica oculto
# Ele será exibido pela função carregar_para_edicao()
# btn_cancelar.grid(row=3, column=2, padx=5, pady=10) # será chamado pela função

# configura o layout para que os campos ocupem mais espaço
frame_entrada.grid_columnconfigure(1, weight=1)

#  Frame de Exibição de Contatos (Treeview)
frame_contatos = ttk.LabelFrame(janela, text="Lista de Contatos")
frame_contatos.pack(padx=10, pady=5, fill="both", expand=True)

# cria o widget Treeview
colunas = ("Nome", "Telefone", "Email")
tree = ttk.Treeview(frame_contatos, columns=colunas, show='headings')

# define os cabeçalhos das colunas
for col in colunas:
    tree.heading(col, text=col)
    tree.column(col, anchor=tk.W, width=150)

# adiciona um scrollbar
scrollbar = ttk.Scrollbar(frame_contatos, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)

tree.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")


#  Botões de Ação na Lista (Editar e Excluir)
frame_botoes_lista = ttk.Frame(janela)
frame_botoes_lista.pack(pady=(0, 10))

btn_editar = ttk.Button(frame_botoes_lista, text="✏️ Editar Contato Selecionado", command=carregar_para_edicao)
btn_editar.pack(side="left", padx=10)

btn_excluir = ttk.Button(frame_botoes_lista, text="❌ Excluir Contato Selecionado", command=excluir_contato)
btn_excluir.pack(side="left", padx=10)


# --- início da aplicação ---

#  Conecta/Cria o DB antes de carregar
conectar_db()[0].close()
# 2. Carrega os contatos existentes ao iniciar a aplicação
carregar_contatos()

# 3. Loop principal da Interface Gráfica
janela.mainloop()