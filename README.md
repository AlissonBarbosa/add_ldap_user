O adiciona_usuario_ldap é um script que tem por objetivo:

 - Adicionar usuários no LDAP de domínios genéricos

A fim de padronizar a entrada de usuários na base de dados do LDAP esse script foi criado.  
Para cada usuário serão necessários preencher os dados básicos como nome, sobrenome, login, senha, o grupo onde o mesmo deve ser adicionado por padrão, por fim a senha de é necessário colocar a credencial de administrador do LDAP para o usuário ser adicionado.

Para rodar o script:
> $ ./adiciona_usuario_ldap.py -c dc=example,dc=com  

Para ajuda:
> $ ./adiciona_usuario_ldap.py -h
