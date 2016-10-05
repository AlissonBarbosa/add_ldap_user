#!/usr/bin/python -tt
# encoding: utf-8

'''Script criado por Alisson Barbosa em setembro de 2016
Tem por objetivo:
    - Criar usuários no ldap para usuarios de dominios genericos'''

from subprocess import call
import subprocess, argparse, os, getpass, sys, string, random

def shell(command):
    '''Funcao que executa comandos shell via python
    Args:
        command (string): Comando shell a ser executado.
    Returns:
        array: Uma lista de strings com a saida do comando shell
    '''
    subcommand = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = subcommand.stdout.read()
    if output.split() == []:
        error = subcommand.stderr.readlines()
        print >>sys.stderr, "ERROR: %s" % error
    else:
        return output

def read_parameter(text):
    '''Funcao que executa um input
    Args:
        text (string): Texto a ser exibido.
    Returns:
        string: Entrada digitada
    '''
    return raw_input(text)

def pass_generate(size, chars):
    '''Funcao que gera uma sequencia de caracteres aleatoria para o caso das senhas nao corresponderem na leitura.
    Args:
        size (integer): numero de caracteres da sequencia
        chars (string): tipos de caracteres desejados - vide documentacao python para o objeto string
    Returns:
        string: Sequencia de caracteres gerada aleatoriamente
    '''
    return ''.join(random.choice(chars) for _ in range(size))

def read_passwd():
    '''Funcao que ler e criptografa a senha do usuario.
    Args:
    Returns:
       string: Senha criptografada
    '''
    passwd = getpass.getpass('Senha: ')
    passwd_confirm = getpass.getpass('Confirme a senha: ')
    if passwd == passwd_confirm:
        return shell("slappasswd -h {SHA} -s %s" % passwd)
    else:
        random_pass = pass_generate(8, string.ascii_uppercase + string.digits + string.ascii_lowercase)
        print "\nSenhas nao correspondem.\nA senha criada aleatoriamente é: %s\nAltere posteriormente."% random_pass
        return shell("slappasswd -h {SHA} -s %s" % random_pass)

def create_id(domain):
    '''Funcao que gera um id para o novo usuario de acordo com o dominio do mesmo.
    Args:
       domain (string): Dominio onde deve ser criado o novo usuario
    Returns:
       string: id do usuario
    '''
    filename = '/tmp/auxid.%s' % os.getpid()
    list_id = open(filename, 'w+b')
    list_id.write(shell('ldapsearch -x -b ou=users,%s "(uidNumber=*)" uidNumber -S uidNumber | grep uidNumber' % domain))
    list_id.close()
    list_id = open(filename, 'r')
    ids = []
    for Id in list_id:
        if Id.split()[0] == "uidNumber:":
            ids.append(int(Id.split()[1]))
    list_id.close()
    os.remove(filename)
    return sorted(ids)[-1] + 1

def group_id(domain):
    '''Funcao que lista os id dos grupos do dominio especificado e recebe a qual deve ser associado o usuario
    Args:
       domain (string): Dominio que deve ser listado os grupos
    Returns:
        string: id do grupo
    '''
    cn = read_parameter("\nDefina o grupo padrao do usuario:\n" + shell('ldapsearch -x -b ou=groups,%s "(gidNumber=*)" cn -S cn | grep cn:' % domain))
    return shell('ldapsearch -x -b ou=groups,%s "(&(objectClass=posixGroup)(cn=%s))" | grep gidNumber:' % (domain, cn))

def create_ldif(domain):
    '''Funcao que cria um ldif com os dados do usuario para ser adicionado ao ldap
    Args:
        domain (string): dn(domain name) a ser adicionado o usuario
    Returns:
        string: Endereço do arquivo salvo com o lif
    '''

    filename = '/tmp/user.ldif'
    user_ldif = open(filename, 'w+b')
    name = read_parameter("Nome do usuario: ")
    surname = read_parameter("Sobrenome do usuario: ")
    login = read_parameter("Login: ")
    passwd = read_passwd()
    uid_number = create_id(domain)
    gid_number = group_id(domain)

    user_ldif.write('dn: cn=%s %s,ou=users,%s\n' % (name, surname, domain))
    user_ldif.write('uid: %s\n' % login)
    user_ldif.write('cn: %s %s\n' % (name, surname))
    user_ldif.write('sn: %s\n' % surname)
    user_ldif.write('mail: %s@example.com\n' % login)
    user_ldif.write('uidNumber: %s\n' % uid_number)
    user_ldif.write('gidNumber: %s' % gid_number)
    user_ldif.write('loginShell: /bin/bash\n')
    user_ldif.write('homeDirectory: /home/%s\n' % login)
    user_ldif.write('userPassword: %s' % passwd)
    user_ldif.write('objectClass: inetOrgPerson\nobjectClass: posixAccount\nobjectClass: top\ntitle: True')
    user_ldif.close()
    add_user(domain, filename)

def add_user(domain, ldif):
    '''Funcao que adiciona o usuario ao LDAP com base do ldif gerado.
    Args:
        ldif: Caminho do arquivo ldif gerado com os dados do usuario
    Returns:
    '''
    print '\nSenha de admin do LDAP: '
    shell("ldapadd -x -D cn=admin,%s -W -f %s" % (domain, ldif))

parser = argparse.ArgumentParser(usage='%(prog)s [options]')
parser.add_argument("-c", help="Indique o dn(domain name) onde o usuario deve ser criado. ex: dc=example,dc=com")
args = parser.parse_args()

if args.c:
    create_ldif(args.c)
