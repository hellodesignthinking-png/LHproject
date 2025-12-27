#!/usr/bin/env python3
"""
Complete updated analyze endpoint with Pipeline Tracer
Apply this to app/api/endpoints/pipeline_reports_v4.py at line ~347
"""

# This is the COMPLETE replacement for the analyze endpoint
# Starting from line 347 to approximately line 574

UPDATED_ANALYZE_ENDPOINT = '''
@router.post("/analyze", response_model=PipelineAnalysisResponse)
async def run_pipeline_analysis(request: PipelineAnalysisRequest):
    """
    Run full 6-MODULE pipeline analysis (with failure tracking)
    
    Executes: M1 (Land Info) → M2 (Appraisal) 🔒 → M3 (LH Demand) 
              → M4 (Capacity) → M5 (Feasibility) → M6 (LH Review)
    
    Returns:
        Comprehensive analysis results with all Context data
    
    Raises:
        PipelineExecutionError: 파이프라인 실행 실패 (상세 정보 포함)
    """
    # 🔥 NEW: Initialize Pipeline Tracer
    tracer = PipelineTracer(parcel_id=request.parcel_id)
    
    try:
        tracer.set_stage(PipelineStage.INIT)
        start_time = time.time()
        
        # Check cache
        if request.use_cache and request.parcel_id in results_cache:
            logger.info(f"✅ Using cached results for {request.parcel_id}")
            cached_result = results_cache[request.parcel_id]
            
            # Extract M4 V2 data from cached result
            capacity_v2 = cached_result.capacity
            legal_units = getattr(capacity_v2.legal_capacity, 'total_units', None) if hasattr(capacity_v2, 'legal_capacity') else None
            incentive_units = getattr(capacity_v2.incentive_capacity, 'total_units', None) if hasattr(capacity_v2, 'incentive_capacity') else None
            massing_count = len(capacity_v2.massing_options) if hasattr(capacity_v2, 'massing_options') else 0
            parking_a = capacity_v2.parking_solutions.get('alternative_A', {}) if hasattr(capacity_v2, 'parking_solutions') else {}
            parking_b = capacity_v2.parking_solutions.get('alternative_B', {}) if hasattr(capacity_v2, 'parking_solutions') else {}
            parking_a_spaces = getattr(parking_a, 'total_parking_spaces', None) if parking_a else None
            parking_b_spaces = getattr(parking_b, 'total_parking_spaces', None) if parking_b else None
            schematics_available = bool(capacity_v2.schematic_drawing_paths) if hasattr(capacity_v2, 'schematic_drawing_paths') else False
            
            tracer.complete()
            
            return PipelineAnalysisResponse(
                parcel_id=request.parcel_id,
                analysis_id=f"cached_{request.parcel_id}",
                status="success",
                execution_time_ms=0,
                modules_executed=6,
                results=pipeline_result_to_dict(cached_result),
                land_value=cached_result.appraisal.land_value,
                confidence_score=cached_result.appraisal.confidence_metrics.confidence_score,
                selected_housing_type=cached_result.housing_type.selected_type,
                recommended_units=cached_result.capacity.unit_summary.total_units,
                npv_public=cached_result.feasibility.financial_metrics.npv_public,
                lh_decision=cached_result.lh_review.decision,
                lh_total_score=cached_result.lh_review.total_score,
                # M4 V2 enhanced outputs
                legal_capacity_units=legal_units,
                incentive_capacity_units=incentive_units,
                massing_options_count=massing_count,
                parking_alt_a_spaces=parking_a_spaces,
                parking_alt_b_spaces=parking_b_spaces,
                schematic_drawings_available=schematics_available
            )
        
        # 🔥 Run pipeline with stage tracking
        logger.info(f"🚀 Running 6-MODULE pipeline for {request.parcel_id}")
        
        # Stage: M1-M6 Pipeline Execution
        tracer.set_stage(PipelineStage.M2)
        
        try:
            result = pipeline.run(request.parcel_id)
        except TimeoutError as e:
            raise tracer.wrap(
                e,
                ReasonCode.EXTERNAL_API_TIMEOUT,
                details={"module": "Pipeline", "timeout_sec": 60}
            )
        except AttributeError as e:
            # Common error: missing M1 data
            if "land" in str(e).lower() or "context" in str(e).lower():
                raise tracer.wrap(
                    e,
                    ReasonCode.MODULE_DATA_MISSING,
                    message_ko="M1 입력 데이터가 누락되었습니다. M1 확정을 먼저 완료해 주세요.",
                    details={"missing_context": "M1", "error": str(e)}
                )
            raise
        
        # Cache results
        results_cache[request.parcel_id] = result
        
        # 🔥 Stage: Data Assembly
        tracer.set_stage(PipelineStage.ASSEMBLE)
        
        # Convert PipelineResult to Phase 3.5D assembled_data format
        context_id = request.parcel_id  # Use parcel_id as context_id
        
        # Build Phase 3.5D assembled_data from pipeline result
        assembled_data = {
            "m6_result": {
                "lh_score_total": result.lh_review.total_score,
                "judgement": result.lh_review.decision,
                "grade": result.lh_review.grade if hasattr(result.lh_review, 'grade') else 'N/A',
                "fatal_reject": False,
                "deduction_reasons": getattr(result.lh_review, 'deduction_reasons', []),
                "improvement_points": getattr(result.lh_review, 'improvement_suggestions', []),
                "section_scores": getattr(result.lh_review, 'section_scores', {})
            },
            "modules": {
                "M2": {
                    "summary": {
                        "land_value": result.appraisal.land_value,
                        "land_value_per_pyeong": result.appraisal.land_value_per_pyeong if hasattr(result.appraisal, 'land_value_per_pyeong') else result.appraisal.land_value / result.land.area_pyeong if result.land.area_pyeong > 0 else 0,
                        "confidence_pct": result.appraisal.confidence_metrics.confidence_score * 100,
                        "appraisal_method": result.appraisal.appraisal_method if hasattr(result.appraisal, 'appraisal_method') else 'standard',
                        "price_range": {
                            "low": result.appraisal.land_value * 0.85,
                            "high": result.appraisal.land_value * 1.15
                        }
                    },
                    "details": {},
                    "raw_data": {}
                },
                "M3": {
                    "summary": {
                        "recommended_type": result.housing_type.selected_type,
                        "total_score": getattr(result.housing_type, 'total_score', 85.0),
                        "demand_score": getattr(result.housing_type, 'demand_score', 90.0),
                        "type_scores": getattr(result.housing_type, 'type_scores', {})
                    },
                    "details": {},
                    "raw_data": {}
                },
                "M4": {
                    "summary": {
                        "total_units": result.capacity.unit_summary.total_units,
                        "incentive_units": getattr(result.capacity, 'incentive_units', result.capacity.unit_summary.total_units),
                        "gross_area_sqm": result.capacity.unit_summary.total_floor_area if hasattr(result.capacity.unit_summary, 'total_floor_area') else 0,
                        "far_used": getattr(result.capacity, 'far_used', 0),
                        "bcr_used": getattr(result.capacity, 'bcr_used', 0)
                    },
                    "details": {},
                    "raw_data": {}
                },
                "M5": {
                    "summary": {
                        "npv_public_krw": result.feasibility.financial_metrics.npv_public,
                        "irr_pct": result.feasibility.financial_metrics.irr * 100 if result.feasibility.financial_metrics.irr else 0,
                        "roi_pct": getattr(result.feasibility.financial_metrics, 'roi', 0) * 100 if hasattr(result.feasibility.financial_metrics, 'roi') else 0,
                        "financial_grade": getattr(result.feasibility, 'grade', 'B'),
                        "total_cost": getattr(result.feasibility, 'total_cost', 0),
                        "total_revenue": getattr(result.feasibility, 'total_revenue', 0)
                    },
                    "details": {},
                    "raw_data": {}
                },
                "M6": {
                    "summary": {
                        "lh_score_total": result.lh_review.total_score,
                        "judgement": result.lh_review.decision,
                        "grade": result.lh_review.grade if hasattr(result.lh_review, 'grade') else 'N/A'
                    },
                    "details": {},
                    "raw_data": {}
                }
            },
            "_frozen": True,
            "_context_id": context_id
        }
        
        # 🔥 Stage: Save
        tracer.set_stage(PipelineStage.SAVE)
        
        # Store in context_storage
        try:
            context_storage.store_frozen_context(
                context_id=context_id,
                land_context=assembled_data,
                ttl_hours=24,
                parcel_id=request.parcel_id
            )
            logger.info(f"✅ Pipeline results saved to context_storage: {context_id}")
        except Exception as storage_err:
            # Storage error shouldn't fail the pipeline completely
            logger.error(f"⚠️ Failed to save to context_storage: {storage_err}")
            raise tracer.wrap(
                storage_err,
                ReasonCode.STORAGE_ERROR,
                details={"context_id": context_id}
            )
        
        # Calculate execution time
        execution_time_ms = (time.time() - start_time) * 1000
        
        # Extract M4 V2 enhanced data
        capacity_v2 = result.capacity  # CapacityContextV2
        legal_units = getattr(capacity_v2.legal_capacity, 'total_units', None) if hasattr(capacity_v2, 'legal_capacity') else None
        incentive_units = getattr(capacity_v2.incentive_capacity, 'total_units', None) if hasattr(capacity_v2, 'incentive_capacity') else None
        massing_count = len(capacity_v2.massing_options) if hasattr(capacity_v2, 'massing_options') else 0
        parking_a = capacity_v2.parking_solutions.get('alternative_A', {}) if hasattr(capacity_v2, 'parking_solutions') else {}
        parking_b = capacity_v2.parking_solutions.get('alternative_B', {}) if hasattr(capacity_v2, 'parking_solutions') else {}
        parking_a_spaces = getattr(parking_a, 'total_parking_spaces', None) if parking_a else None
        parking_b_spaces = getattr(parking_b, 'total_parking_spaces', None) if parking_b else None
        schematics_available = bool(capacity_v2.schematic_drawing_paths) if hasattr(capacity_v2, 'schematic_drawing_paths') else False
        
        # Build response
        response = PipelineAnalysisResponse(
            parcel_id=request.parcel_id,
            analysis_id=generate_analysis_id(request.parcel_id),
            status="success" if result.success else "failed",
            execution_time_ms=execution_time_ms,
            modules_executed=6,
            results=pipeline_result_to_dict(result),
            land_value=result.appraisal.land_value,
            confidence_score=result.appraisal.confidence_metrics.confidence_score,
            selected_housing_type=result.housing_type.selected_type,
            recommended_units=result.capacity.unit_summary.total_units,
            npv_public=result.feasibility.financial_metrics.npv_public,
            lh_decision=result.lh_review.decision,
            lh_total_score=result.lh_review.total_score,
            # M4 V2 enhanced outputs
            legal_capacity_units=legal_units,
            incentive_capacity_units=incentive_units,
            massing_options_count=massing_count,
            parking_alt_a_spaces=parking_a_spaces,
            parking_alt_b_spaces=parking_b_spaces,
            schematic_drawings_available=schematics_available
        )
        
        logger.info(f"✅ Pipeline completed in {execution_time_ms:.0f}ms")
        tracer.complete()
        return response
        
    except DataValidationError as e:
        # Data validation failed
        raise tracer.wrap(
            e,
            ReasonCode.DATA_BINDING_MISSING,
            details={"validation_errors": getattr(e, 'technical_message', str(e))}
        )
    
    except DataBindingError as e:
        # Data binding failed
        raise tracer.wrap(
            e,
            ReasonCode.DATA_BINDING_MISSING,
            details={
                "missing_paths": getattr(e, 'missing_paths', []),
                "error": str(e)
            }
        )
    
    except PipelineExecutionError:
        # Already wrapped by tracer, just re-raise
        raise
    
    except Exception as e:
        # Unknown error - wrap it
        logger.error(f"❌ Pipeline analysis failed: {str(e)}", exc_info=True)
        raise tracer.wrap(
            e,
            ReasonCode.UNKNOWN,
            details={
                "error_type": type(e).__name__,
                "parcel_id": request.parcel_id
            }
        )
'''

print("✅ Updated endpoint code generated")
print("\n📝 Manual steps:")
print("1. Open app/api/endpoints/pipeline_reports_v4.py")
print("2. Find @router.post('/analyze') at line ~347")
print("3. Replace entire function (up to line ~574) with code above")
print("4. Test with: curl -X POST /api/v4/pipeline/analyze -d '{\"parcel_id\": \"test-001\"}'")
