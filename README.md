# Implementação de uma Matching Engine

## Introdução

Uma **Matching Engine** (ou **Order Matching System**) é um sistema que cruza ordens de compra e venda de ativos financeiros, garantindo execuções justas e eficientes. Esta implementação atende aos requisitos especificados no teste técnico, incluindo todos os itens da seção bônus.

## Requisitos

A engine foi projetada com as seguintes premissas:

- Trabalha com **apenas um ativo**.
- Suporta dois tipos de ordens:
  - **Limit Order**: ordem colocada a um preço fixo.
  - **Market Order**: ordem executada ao melhor preço disponível.
- Os dados são armazenados **em memória volátil**.
- Não há preocupação com **escalabilidade ou infraestrutura em nuvem**.
- O comportamento das ordens foi definido para **garantir prioridade temporal** (FIFO).

## Funcionamento

A implementação segue a lógica de um **livro de ofertas** (order book), onde ordens são organizadas e cruzadas conforme chegam ao sistema.

- **Ordens limit** são inseridas no livro se não puderem ser executadas imediatamente.
- **Ordens market** são imediatamente preenchidas ao melhor preço disponível.
- **Ordem de chegada é respeitada**: ordens mais antigas são executadas primeiro.
- **Ordens limit inválidas** (que gerariam um trade imediato) podem ser executadas ou rejeitadas, dependendo da configuração escolhida.

### Estrutura do Livro de Ofertas

O livro de ofertas é estruturado da seguinte forma:

- **Ordens de compra** são organizadas em ordem decrescente de preço (melhores ofertas no topo).
- **Ordens de venda** são organizadas em ordem crescente de preço (menores preços no topo).
- **Market orders** consomem ordens do lado oposto no melhor preço disponível.

### Exemplo de Entrada e Saída

```plaintext
>>> limit buy 10 100
>>> limit sell 20 100
>>> limit sell 20 200
>>> market buy 150
Trade, price: 20, qty: 150
>>> market buy 200
Trade, price: 20, qty: 150
>>> market sell 200
Trade, price: 10, qty: 100
```

## Melhorias e Correções

1. Agora, todas as ordens criadas enquanto o comércio estava pausado são executadas de acordo com sua prioridade. Antes, apenas a última ordem criada era executada quando o comércio era retomado.
2. Documentação mais detalhada.
3. Separação das classes em diferentes arquivos.

## Tecnologias e Escolhas de Desenvolvimento

A solução foi desenvolvida em **Python**, pois é a linguagem com a qual tenho mais familiaridade. Embora não seja ideal para trabalhar com **POO**, foi suficiente para deixar o código mais legível e simples.

A interação com o programa é feita por meio da **linha de comando**. Para executar:

```sh
python main.py
```

Para obter ajuda, basta digitar `help` no terminal.

## Recursos Implementados (Bônus)

### 1. Visualização do Livro de Ofertas

- `print book`: Exibe todas as ordens ativas, bid e offer price.
- `print order <order_id>`: Obtém mais informações sobre uma ordem específica.
- `print filled`: Exibe todas as ordens já preenchidas.

### 2. Respeito à Ordem de Chegada (FIFO)

Utilizei **dicionários** para armazenar as ordens à medida que são criadas. Assim como os vetores, em Python, os dicionários **preservam a ordem de adição**, garantindo que a prioridade seja respeitada durante a iteração.

O uso de dicionários, aliado a um **ID único** como chave para cada nova ordem, melhora a performance, pois a busca de qualquer ordem é feita em **O(1)**, evitando percorrer todo o array para encontrar um item específico.

### 3. Cancelamento de Ordens

Uma ordem pode ser cancelada utilizando seu **ID**.

```plaintext
>>> limit buy 10 100
Order created: buy 100 @ 10 identificador_1
>>> cancel order identificador_1
Order cancelled
```

### 4. Modificação de Ordens

O ID da ordem também é utilizado para **modificar** suas informações.

```plaintext
>>> modify order identificador_1 price 9.98
```

### 5. Pegged Orders

Ordens pegged possuem preços dinâmicos que acompanham o **bid** (melhor preço de compra) ou o **offer** (melhor preço de venda). Para isso, a implementação utiliza atributos de classe que são atualizados sempre que uma ordem é adicionada ou removida do livro.

```plaintext
>>> peg bid buy 150
```

## Complexidade Computacional

A função que mais se afasta da complexidade linear é a que **ordena os dicionários** para execução de ordens do tipo market. Para isso, utilizei a função `sorted()`, que possui complexidade **O(n log n)** na maioria dos casos, mantendo-se eficiente dentro do contexto proposto.

## Conclusão

A implementação segue boas práticas de estruturação de dados e engenharia de software, garantindo uma solução eficiente para o problema proposto. O código respeita a ordem de chegada das ordens, permite visualização do livro, cancelamento e modificação de ordens, além de suportar ordens pegged.
