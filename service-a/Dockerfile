FROM golang

WORKDIR /app

COPY go.mod ./
COPY *.go ./

RUN CGO_ENABLED=0 GOOS=linux go build -o /service-a

EXPOSE 8888

CMD ["/service-a"]