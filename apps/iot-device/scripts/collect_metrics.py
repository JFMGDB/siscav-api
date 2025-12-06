"""Script para coletar e analisar métricas de desempenho do sistema."""

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List


def parse_logs(log_file: str) -> Dict:
    """
    Analisa logs e extrai métricas de desempenho.

    Args:
        log_file: Caminho para o arquivo de log

    Returns:
        Dicionário com métricas extraídas
    """
    metrics = {
        "total_detections": 0,
        "successful_ocr": 0,
        "failed_ocr": 0,
        "api_success": 0,
        "api_failures": 0,
        "api_timeouts": 0,
        "authorized_count": 0,
        "denied_count": 0,
        "plates_detected": [],
        "detection_times": [],
        "errors": [],
        "start_time": None,
        "end_time": None,
    }

    time_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                # Extrair timestamp
                time_match = time_pattern.search(line)
                if time_match and not metrics["start_time"]:
                    metrics["start_time"] = time_match.group(1)

                if time_match:
                    metrics["end_time"] = time_match.group(1)

                # Contar detecções
                if "Placa detectada:" in line:
                    metrics["total_detections"] += 1
                    # Extrair placa
                    plate_match = re.search(r"Placa detectada: (\w+)", line)
                    if plate_match:
                        metrics["plates_detected"].append(plate_match.group(1))

                # Contar OCR bem-sucedido
                if "Placa detectada:" in line and "None" not in line:
                    metrics["successful_ocr"] += 1

                # Contar falhas de OCR (placa não detectada após processamento)
                if "Erro" in line and "OCR" in line:
                    metrics["failed_ocr"] += 1

                # Contar sucessos de API
                if "Resposta da API: Authorized" in line:
                    metrics["api_success"] += 1
                    metrics["authorized_count"] += 1
                elif "Resposta da API: Denied" in line:
                    metrics["api_success"] += 1
                    metrics["denied_count"] += 1

                # Contar falhas de API
                if "Erro ao enviar dados para API" in line:
                    metrics["api_failures"] += 1
                    if "Timeout" in line or "timeout" in line:
                        metrics["api_timeouts"] += 1

                # Coletar erros
                if "ERROR" in line or "Erro" in line:
                    error_msg = line.strip()
                    if error_msg not in metrics["errors"]:
                        metrics["errors"].append(error_msg)

    except FileNotFoundError:
        print(f"Erro: Arquivo de log não encontrado: {log_file}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao processar log: {e}", file=sys.stderr)
        sys.exit(1)

    return metrics


def calculate_statistics(metrics: Dict) -> Dict:
    """
    Calcula estatísticas adicionais a partir das métricas.

    Args:
        metrics: Dicionário com métricas básicas

    Returns:
        Dicionário com estatísticas calculadas
    """
    stats = {}

    # Taxa de sucesso de OCR
    total_ocr_attempts = metrics["successful_ocr"] + metrics["failed_ocr"]
    if total_ocr_attempts > 0:
        stats["ocr_success_rate"] = (metrics["successful_ocr"] / total_ocr_attempts) * 100
    else:
        stats["ocr_success_rate"] = 0.0

    # Taxa de sucesso da API
    total_api_attempts = metrics["api_success"] + metrics["api_failures"]
    if total_api_attempts > 0:
        stats["api_success_rate"] = (metrics["api_success"] / total_api_attempts) * 100
    else:
        stats["api_success_rate"] = 0.0

    # Taxa de autorização
    total_responses = metrics["authorized_count"] + metrics["denied_count"]
    if total_responses > 0:
        stats["authorization_rate"] = (metrics["authorized_count"] / total_responses) * 100
    else:
        stats["authorization_rate"] = 0.0

    # Placas únicas detectadas
    stats["unique_plates"] = len(set(metrics["plates_detected"]))

    # Duração da sessão (se timestamps disponíveis)
    if metrics["start_time"] and metrics["end_time"]:
        try:
            start = datetime.strptime(metrics["start_time"], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(metrics["end_time"], "%Y-%m-%d %H:%M:%S")
            duration = (end - start).total_seconds()
            stats["session_duration_seconds"] = duration

            # Detecções por minuto
            if duration > 0:
                stats["detections_per_minute"] = (metrics["total_detections"] / duration) * 60
            else:
                stats["detections_per_minute"] = 0.0
        except ValueError:
            stats["session_duration_seconds"] = None
            stats["detections_per_minute"] = None
    else:
        stats["session_duration_seconds"] = None
        stats["detections_per_minute"] = None

    return stats


def generate_report(metrics: Dict, stats: Dict, output_file: str = None) -> str:
    """
    Gera relatório formatado das métricas.

    Args:
        metrics: Métricas básicas
        stats: Estatísticas calculadas
        output_file: Arquivo para salvar relatório (opcional)

    Returns:
        String com relatório formatado
    """
    report = []
    report.append("=" * 60)
    report.append("RELATÓRIO DE DESEMPENHO - SISCAV IoT DEVICE")
    report.append("=" * 60)
    report.append("")

    # Métricas Gerais
    report.append("MÉTRICAS GERAIS")
    report.append("-" * 60)
    report.append(f"Total de Detecções: {metrics['total_detections']}")
    report.append(f"Placas Únicas: {stats['unique_plates']}")
    report.append(f"OCR Bem-sucedido: {metrics['successful_ocr']}")
    report.append(f"OCR Falhou: {metrics['failed_ocr']}")
    report.append(f"Taxa de Sucesso OCR: {stats['ocr_success_rate']:.2f}%")
    report.append("")

    # API
    report.append("COMUNICAÇÃO COM API")
    report.append("-" * 60)
    report.append(f"Requisições Bem-sucedidas: {metrics['api_success']}")
    report.append(f"Requisições Falhadas: {metrics['api_failures']}")
    report.append(f"Timeouts: {metrics['api_timeouts']}")
    report.append(f"Taxa de Sucesso API: {stats['api_success_rate']:.2f}%")
    report.append("")

    # Autorizações
    report.append("AUTORIZAÇÕES")
    report.append("-" * 60)
    report.append(f"Autorizadas: {metrics['authorized_count']}")
    report.append(f"Negadas: {metrics['denied_count']}")
    report.append(f"Taxa de Autorização: {stats['authorization_rate']:.2f}%")
    report.append("")

    # Sessão
    if stats["session_duration_seconds"]:
        report.append("SESSÃO")
        report.append("-" * 60)
        report.append(f"Duração: {stats['session_duration_seconds']:.2f} segundos")
        if stats["detections_per_minute"]:
            report.append(f"Detecções por Minuto: {stats['detections_per_minute']:.2f}")
        report.append("")

    # Erros
    if metrics["errors"]:
        report.append("ERROS ENCONTRADOS")
        report.append("-" * 60)
        for error in metrics["errors"][:10]:  # Limitar a 10 erros
            report.append(f"  - {error}")
        if len(metrics["errors"]) > 10:
            report.append(f"  ... e mais {len(metrics['errors']) - 10} erros")
        report.append("")

    # Placas Detectadas
    if metrics["plates_detected"]:
        report.append("PLACAS DETECTADAS")
        report.append("-" * 60)
        plate_counts = defaultdict(int)
        for plate in metrics["plates_detected"]:
            plate_counts[plate] += 1

        for plate, count in sorted(plate_counts.items(), key=lambda x: x[1], reverse=True):
            report.append(f"  {plate}: {count} vez(es)")
        report.append("")

    report.append("=" * 60)

    report_text = "\n".join(report)

    if output_file:
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report_text)
            print(f"Relatório salvo em: {output_file}")
        except Exception as e:
            print(f"Erro ao salvar relatório: {e}", file=sys.stderr)

    return report_text


def main():
    """Função principal do script."""
    parser = argparse.ArgumentParser(
        description="Coleta e analisa métricas de desempenho do sistema SISCAV"
    )
    parser.add_argument(
        "log_file",
        type=str,
        help="Caminho para o arquivo de log a ser analisado",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Arquivo para salvar relatório (opcional)",
    )
    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        help="Saída em formato JSON",
    )

    args = parser.parse_args()

    # Verificar se arquivo existe
    if not Path(args.log_file).exists():
        print(f"Erro: Arquivo não encontrado: {args.log_file}", file=sys.stderr)
        sys.exit(1)

    # Processar logs
    metrics = parse_logs(args.log_file)
    stats = calculate_statistics(metrics)

    # Gerar saída
    if args.json:
        output = {
            "metrics": metrics,
            "statistics": stats,
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        report = generate_report(metrics, stats, args.output)
        print(report)


if __name__ == "__main__":
    main()













