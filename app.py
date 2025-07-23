import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# กำหนด page config
st.set_page_config(
    page_title="Affiliate Ad Campaign Planner",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS สำหรับปรับแต่ง UI
st.markdown("""
<style>
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin: 0.5rem 0;
}
.metric-value {
    font-size: 2rem;
    font-weight: bold;
    margin: 0.5rem 0;
}
.metric-label {
    font-size: 0.9rem;
    opacity: 0.8;
}
.recommendation-box {
    background: #f8f9ff;
    border: 1px solid #e6e8ff;
    border-radius: 10px;
    padding: 1rem;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.title("📈 Affiliate Ad Campaign Planner")
    st.markdown("**วางแผนการยิงแอดอย่างชาญฉลาด เพิ่มผลตอบแทนสูงสุด**")
    st.divider()
    
    # Sidebar สำหรับ input
    with st.sidebar:
        st.header("🎯 เป้าหมายการแคมเปญ")
        target_orders = st.number_input(
            "เป้าหมายจำนวนออเดอร์",
            min_value=1,
            value=100,
            help="ระบุจำนวนออเดอร์ที่ต้องการ"
        )
        
        bonus_amount = st.number_input(
            "โบนัสที่จะได้รับ (บาท)",
            min_value=0.0,
            value=5000.0,
            help="ระบุจำนวนโบนัสที่จะได้รับเพิ่ม"
        )
        
        st.divider()
        
        st.header("📁 อัพโหลดรายงานผล")
        uploaded_file = st.file_uploader(
            "เลือกไฟล์ CSV",
            type=['csv'],
            help="อัพโหลดไฟล์รายงานผลการทำแอดที่ผ่านมา"
        )
    
    # Main content
    if uploaded_file is not None:
        try:
            # อ่านข้อมูล CSV
            df = pd.read_csv(uploaded_file)
            
            # แสดงข้อมูลพื้นฐาน
            with st.expander("📋 ดูข้อมูลที่อัพโหลด", expanded=False):
                st.dataframe(df, use_container_width=True)
                st.info(f"โหลดข้อมูลสำเร็จ: {len(df)} รายการ")
            
            # ทำความสะอาดข้อมูล
            df_clean = df[
                (df['Order Count'] > 0) & 
                (df['Ad Cost'] > 0) &
                df['Order Count'].notna() &
                df['Ad Cost'].notna()
            ].copy()
            
            if len(df_clean) == 0:
                st.error("❌ ไม่มีข้อมูลที่ใช้ได้สำหรับการคำนวณ")
                return
            
            # คำนวณค่าเฉลี่ย
            avg_cpc = df_clean['CPC(Link)'].mean()
            avg_cost_per_order = df_clean['Cost Per Order(Shopee)'].mean()
            avg_commission_rate = (df_clean['Total Com'] / df_clean['Ad Cost']).mean()
            
            # คำนวณการประมาณการ
            estimated_ad_cost = target_orders * avg_cost_per_order
            estimated_commission = estimated_ad_cost * avg_commission_rate
            net_profit = estimated_commission + bonus_amount - estimated_ad_cost
            roi = (net_profit / estimated_ad_cost) * 100
            
            # แสดงผลสรุป
            st.header("💰 สรุปการวิเคราะห์")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div class="metric-card" style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);">
                    <div class="metric-label">งบโฆษณาที่ต้องใช้</div>
                    <div class="metric-value">฿{:,.0f}</div>
                </div>
                """.format(estimated_ad_cost), unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                    <div class="metric-label">ค่าคอมที่คาดว่าจะได้</div>
                    <div class="metric-value">฿{:,.0f}</div>
                </div>
                """.format(estimated_commission), unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="metric-card" style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);">
                    <div class="metric-label">กำไรสุทธิ</div>
                    <div class="metric-value">฿{:,.0f}</div>
                </div>
                """.format(net_profit), unsafe_allow_html=True)
            
            with col4:
                color = "#10b981" if roi >= 0 else "#ef4444"
                st.markdown("""
                <div class="metric-card" style="background: linear-gradient(135deg, {0} 0%, {0} 100%);">
                    <div class="metric-label">ROI คาดการณ์</div>
                    <div class="metric-value">{1:.1f}%</div>
                </div>
                """.format(color, roi), unsafe_allow_html=True)
            
            # กราฟแสดง ROI ของแต่ละ Sub ID
            st.header("📊 การวิเคราะห์ผลการดำเนินงาน")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # กราฟ ROI
                fig_roi = px.bar(
                    df_clean.head(10), 
                    x='Sub_id4', 
                    y='ROI (%)',
                    title="ROI ของ Sub ID (Top 10)",
                    color='ROI (%)',
                    color_continuous_scale='RdYlGn'
                )
                fig_roi.update_layout(
                    xaxis_tickangle=-45,
                    height=400
                )
                st.plotly_chart(fig_roi, use_container_width=True)
            
            with col2:
                # กราฟ Order Count vs Ad Cost
                fig_scatter = px.scatter(
                    df_clean,
                    x='Ad Cost',
                    y='Order Count',
                    size='Total Com',
                    color='ROI (%)',
                    hover_data=['Sub_id4'],
                    title="ความสัมพันธ์ Cost vs Orders",
                    color_continuous_scale='RdYlGn'
                )
                fig_scatter.update_layout(height=400)
                st.plotly_chart(fig_scatter, use_container_width=True)
            
            # แนะนำการกระจายงบ
            st.header("🎯 แนะนำการกระจายงบโฆษณา")
            
            # หา Top Performers
            top_performers = df_clean.nlargest(5, 'ROI (%)').copy()
            
            # คำนวณการกระจายงบ
            weights = [0.35, 0.25, 0.20, 0.12, 0.08]  # น้ำหนักการกระจายงบ
            
            recommendations = []
            for i, (idx, row) in enumerate(top_performers.iterrows()):
                allocated_budget = estimated_ad_cost * weights[i]
                expected_orders = int(allocated_budget / row['Cost Per Order(Shopee)'])
                
                recommendations.append({
                    'Sub ID': row['Sub_id4'],
                    'งบที่แนะนำ (บาท)': f"฿{allocated_budget:,.0f}",
                    'ออเดอร์คาดการณ์': f"{expected_orders:,} ออเดอร์",
                    'ROI ในอดีต (%)': f"{row['ROI (%)']:.1f}%",
                    'เปอร์เซ็นต์งบ': f"{weights[i]*100:.0f}%"
                })
            
            recommendations_df = pd.DataFrame(recommendations)
            st.dataframe(recommendations_df, use_container_width=True, hide_index=True)
            
            # ข้อมูลเพิ่มเติม
            st.header("📈 ค่าเฉลี่ยจากข้อมูลในอดีต")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="CPC เฉลี่ย",
                    value=f"฿{avg_cpc:.2f}",
                    help="ค่าใช้จ่ายเฉลี่ยต่อการคลิก"
                )
            
            with col2:
                st.metric(
                    label="ต้นทุนต่อออเดอร์",
                    value=f"฿{avg_cost_per_order:.2f}",
                    help="ค่าใช้จ่ายเฉลี่ยต่อออเดอร์ที่ได้"
                )
            
            with col3:
                st.metric(
                    label="อัตราค่าคอม",
                    value=f"{avg_commission_rate*100:.1f}%",
                    help="เปอร์เซ็นต์ค่าคอมเฉลี่ยต่อค่าโฆษณา"
                )
            
            # คำแนะนำ
            st.header("💡 คำแนะนำจากการวิเคราะห์")
            
            recommendation_text = f"""
            <div class="recommendation-box">
            <h4>🎯 สรุปแผนการลงทุน:</h4>
            <ul>
                <li><strong>งบโฆษณาที่ควรใช้:</strong> ฿{estimated_ad_cost:,.0f}</li>
                <li><strong>ผลตอบแทนคาดการณ์:</strong> ฿{estimated_commission + bonus_amount:,.0f} (ค่าคอม + โบนัส)</li>
                <li><strong>กำไรสุทธิ:</strong> ฿{net_profit:,.0f}</li>
                <li><strong>ROI:</strong> {roi:.1f}%</li>
            </ul>
            
            <h4>📊 กลยุทธ์การกระจายงบ:</h4>
            <ul>
                <li>ควรโฟกัสที่ Sub ID ที่มี ROI สูงกว่า 0%</li>
                <li>กระจายงบให้ Sub ID ที่มีผลงานดีมากขึ้น (35% สำหรับอันดับ 1)</li>
                <li>เริ่มด้วยงบเล็กๆ ในอันดับต่ำๆ เพื่อทดสอบประสิทธิภาพ</li>
            </ul>
            </div>
            """
            
            if roi >= 20:
                recommendation_text += """
                <div style="background: #dcfce7; border: 1px solid #16a34a; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                    <h4 style="color: #16a34a;">✅ สถานะ: ดีมาก</h4>
                    <p>ROI คาดการณ์อยู่ในระดับที่ดีมาก ควรดำเนินการตามแผนได้เลย</p>
                </div>
                """
            elif roi >= 0:
                recommendation_text += """
                <div style="background: #fef3c7; border: 1px solid #d97706; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                    <h4 style="color: #d97706;">⚠️ สถานะ: ปานกลาง</h4>
                    <p>ROI เป็นบวกแต่ไม่สูงมาก ควรพิจารณาปรับกลยุทธ์หรือลดความเสี่ยง</p>
                </div>
                """
            else:
                recommendation_text += """
                <div style="background: #fee2e2; border: 1px solid #dc2626; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                    <h4 style="color: #dc2626;">❌ สถานะ: เสี่ยง</h4>
                    <p>ROI เป็นลบ ควรทบทวนเป้าหมายหรือเลือก Sub ID ที่มีประสิทธิภาพดีกว่า</p>
                </div>
                """
            
            st.markdown(recommendation_text, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาดในการประมวลผลข้อมูล: {str(e)}")
            st.info("💡 ตรวจสอบให้แน่ใจว่าไฟล์ CSV มีคอลัมน์ที่จำเป็น: Sub_id4, Ad Cost, Order Count, Total Com, ROI (%), CPC(Link), Cost Per Order(Shopee)")
    
    else:
        # แสดงข้อมูลตัวอย่างเมื่อยังไม่ได้อัพโหลดไฟล์
        st.info("📁 กรุณาอัพโหลดไฟล์ CSV รายงานผลการทำแอดในแถบด้านซ้าย")
        
        with st.expander("📝 ตัวอย่างรูปแบบไฟล์ CSV ที่รองรับ", expanded=True):
            sample_data = {
                'Sub_id4': ['m06Nasa1228', 'm02Rooftop0623', 'm56ErgoSleep0420'],
                'Ad Cost': [67.57, 2000.00, 397.68],
                'Shopee Com': [49.89, 613.08, 207.74],
                'Lazada Com': [0.00, 469.97, 4.63],
                'Total Com': [49.89, 1083.05, 212.37],
                'Profit': [-17.68, -916.95, -185.31],
                'ROI (%)': [-26.17, -45.85, -46.60],
                'Link Click': [56, 1184, 67],
                'Order Count': [4, 82, 7],
                'CPC(Link)': [1.21, 1.69, 5.94],
                'Cost Per Order(Shopee)': [16.89, 24.39, 56.81]
            }
            sample_df = pd.DataFrame(sample_data)
            st.dataframe(sample_df, use_container_width=True)

if __name__ == "__main__":
    main()