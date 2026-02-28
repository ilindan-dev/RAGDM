# 1: Builder
FROM golang:1.25-bookworm AS builder

# Install instruments CGO
RUN apt-get update && apt-get install -y cmake clang

WORKDIR /app

COPY backend/go.mod backend/go.sum ./backend/
RUN cd backend && go mod download

COPY algorithm/ ./algorithm/
COPY backend/ ./backend/

WORKDIR /app/backend
RUN CGO_ENABLED=1 GOOS=linux go build -o /ragdm_app ./cmd/main.go

# 2: Final runtime image
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y ca-certificates libc6 && rm -rf /var/lib/apt/lists/*

WORKDIR /root/

COPY --from=builder /ragdm_app .

COPY frontend/ ./frontend/

EXPOSE 8080

CMD ["./ragdm_app"]