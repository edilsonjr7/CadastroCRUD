create database escola;
use escola;

create table curso (
id_curso int primary key auto_increment,
nome_curso varchar (30),
descricao varchar(500), 
duracao int
);

create table alunos (
id_aluno int primary key auto_increment,
nome varchar(100) not null,
cpf varchar(11),
tel varchar(14),
email varchar (40),
id_curso int,
foreign key (id_curso) references curso(id_curso)
);

select * from curso;
select * from alunos;





